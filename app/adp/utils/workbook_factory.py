from dotenv import load_dotenv

load_dotenv()
import os
import pandas as pd
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Iterable
from datetime import datetime
from openpyxl.styles import Font, Alignment, numbers
from app.adp.adp_models import Fields
from app.adp.utils.programs import (
    CoilProgram,
    AirHandlerProgram,
    CustomerProgram,
    EmptyProgram,
)
from app.adp.utils.pricebook import PriceBook
from app.db import Session, ADP_DB, SCA_DB, Stage, DB_V2


logger = logging.getLogger("uvicorn.info")
TODAY = str(datetime.today().date())
TEMPLATES = os.getenv("TEMPLATES")


class AttrType(Enum):
    NUMBER = int
    STRING = str


@dataclass
class ProgramFile:
    file_name: str
    file_data: bytes


def build_coil_program(
    program_data: pd.DataFrame, ratings: pd.DataFrame
) -> CoilProgram:
    program_data = program_data.drop(columns=["customer_id"])
    program_data = program_data.sort_values(
        by=[
            Fields.CATEGORY.value,
            Fields.SERIES.value,
            Fields.MPG.value,
            Fields.METERING.value,
            Fields.TONNAGE.value,
            Fields.WIDTH.value,
            Fields.HEIGHT.value,
        ]
    ).drop_duplicates()
    prog_ratings = ratings.drop(columns=[Fields.CUSTOMER_ID.value])
    return CoilProgram(program_data=program_data, ratings=prog_ratings)


def build_ah_program(
    program_data: pd.DataFrame, ratings: pd.DataFrame
) -> AirHandlerProgram:
    program_data = program_data.drop(columns=["customer_id"])
    temp_heat_num_col = "heat_num"
    program_data[temp_heat_num_col] = (
        program_data[Fields.HEAT.value]
        .str.extract(r"(\d+|\d\.\d)\s*kW")
        .fillna(0)
        .astype(float)
        .astype(int)
    )
    program_data = program_data.sort_values(
        by=[
            Fields.CATEGORY.value,
            Fields.SERIES.value,
            Fields.MPG.value,
            Fields.TONNAGE.value,
            Fields.WIDTH.value,
            temp_heat_num_col,
        ]
    ).drop_duplicates()
    program_data = program_data.drop(columns=[temp_heat_num_col])
    prog_ratings = ratings.drop(columns=[Fields.CUSTOMER_ID.value])
    return AirHandlerProgram(program_data=program_data, ratings=prog_ratings)


def pull_customer_payment_terms_v2(session: Session, customer_id: int) -> pd.DataFrame:
    sql_attrs = """
        SELECT vendor_customers.id AS customer_id, vendor_customer_attrs.id as attr_id,
            attr, value, type  
        FROM vendor_customers 
        JOIN vendor_customer_attrs 
        ON vendor_customer_attrs.vendor_customer_id = vendor_customers.id
        WHERE attr in ('ppf','terms')
        AND vendor_id = 'adp'
        AND vendor_customer_attrs.deleted_at IS NULL
        AND vendor_customers.id = :customer_id;
    """
    customer_attrs = DB_V2.execute(session, sql_attrs, {"customer_id": customer_id})
    customer_attrs_df = pd.DataFrame(
        customer_attrs.fetchall(), columns=customer_attrs.keys()
    )

    attr_ids = tuple(customer_attrs_df["attr_id"].to_list())
    attr_types_by_col = customer_attrs_df[["attr", "type"]]
    sql_last_eff_date_by_customer = """
        SELECT b.id AS customer_id, DATE_TRUNC('second',max(timestamp)) AS effective_date
        FROM vendor_customer_attrs_changelog
        JOIN vendor_customer_attrs AS a
        ON a.id = attr_id
        JOIN vendor_customers AS b
        ON b.id = a.vendor_customer_id
        WHERE attr_id IN :attr_ids
        GROUP BY b.id;
    """
    customer_latest_effective_date = DB_V2.execute(
        session, sql_last_eff_date_by_customer, {"attr_ids": attr_ids}
    ).one()[-1]

    # ought to be a one-row table now
    customer_attrs_df = customer_attrs_df.pivot(
        index="customer_id", columns="attr", values="value"
    )
    customer_attrs_df["effective_date"] = customer_latest_effective_date
    for attr in attr_types_by_col.itertuples():
        customer_attrs_df[attr.attr] = customer_attrs_df[attr.attr].astype(
            AttrType[attr.type].value
        )

    customer_attrs_df = customer_attrs_df.infer_objects()
    return customer_attrs_df


def pull_customer_payment_terms(session: Session, customer_id: int) -> pd.DataFrame:

    try:
        # NOTE temporarily wrapping this in try-except to fallback in v1 tables
        # In my inifinte wisdown, I pushed this functionality half-baked and before
        # the migration had been executed.
        return pull_customer_payment_terms_v2(session, customer_id)
    except:
        return ADP_DB.load_df(
            session=session,
            table_name="customer_terms_by_customer_id",
            customer_id=customer_id,
        )


def pull_customer_parts(session: Session, customer_id: int) -> pd.DataFrame:
    return ADP_DB.load_df(
        session=session, table_name="program_parts_expanded", customer_id=customer_id
    )


def pull_customer_alias_mapping(session: Session) -> pd.DataFrame:
    return ADP_DB.load_df(session=session, table_name="customers")


def pull_customer_parent_accounts(session: Session) -> pd.DataFrame:
    return SCA_DB.load_df(session=session, table_name="customers")


def add_customer_terms_parts_and_logo_path(
    session: Session,
    customer_id: int,
    coil_prog: CoilProgram,
    ah_prog: AirHandlerProgram,
) -> CustomerProgram:

    footer = pull_customer_payment_terms(session, customer_id)
    prog_parts = pull_customer_parts(session, customer_id)
    alias_mapping = pull_customer_alias_mapping(session)
    parent_accounts = pull_customer_parent_accounts(session)

    alias_mapping = alias_mapping[alias_mapping["id"] == customer_id]
    alias_name = alias_mapping[Fields.ADP_ALIAS.value].item()
    ## parts
    customer_parts = prog_parts.drop(columns="customer_id")
    customer_preferred = alias_mapping["preferred_parts"].item() == True
    ## specific column name for pricing is to be set
    if customer_preferred:
        part_price_col = "preferred"
        # some "preferred" pricing is left blank,
        # so default the price to standard pricing
        customer_parts[part_price_col] = customer_parts[part_price_col].fillna(
            customer_parts["standard"]
        )
    else:
        part_price_col = "standard"
    customer_parts = customer_parts[
        ["description", "part_number", "pkg_qty", part_price_col]
    ]
    ## footer
    try:
        payment_terms = footer["terms"].item()
        pre_paid_freight = footer["ppf"].item()
        effective_date = str(footer["effective_date"].item())
    except:
        logger.info(f"footer capture failed for {alias_name}")
        payment_terms = None
        pre_paid_freight = None
        effective_date = "1900-01-01 00:00:00"
    terms = {
        "Payment Terms": {
            "value": payment_terms,
            "style": {
                "font": Font(bold=True),
                "alignment": Alignment(horizontal="right"),
            },
        },
        "Freight": {
            "value": pre_paid_freight,
            "style": {
                "number_format": numbers.FORMAT_CURRENCY_USD,
                "font": Font(bold=True),
                "alignment": Alignment(horizontal="right"),
            },
        },
        "Effective Date": {
            "value": datetime.strptime(effective_date, r"%Y-%m-%d %H:%M:%S"),
            "style": {
                "font": Font(bold=True),
                "alignment": Alignment(horizontal="right"),
                "number_format": numbers.FORMAT_DATE_YYYYMMDD2,
            },
        },
    }
    ## logo_path
    customer_sca_id = parent_accounts["id"] == alias_mapping["sca_id"].item()
    logo_filename = parent_accounts.loc[customer_sca_id, "logo"].item()
    if not logo_filename:
        logo_filename = ""
    full_logo_path = logo_filename
    return CustomerProgram(
        customer_id=customer_id,
        customer_name=alias_name,
        coils=coil_prog,
        air_handlers=ah_prog,
        parts=customer_parts,
        terms=terms,
        logo_path=full_logo_path,
    )


def pull_program_data_v2(
    session: Session, customer_id: int
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sql_pricing = """
        SELECT id, product_id, price
        FROM vendor_pricing_by_customer
        WHERE vendor_customer_id = :customer_id"""
    sql_product = """"""
    sql_product_attrs = """"""
    sql_ratings = """"""
    return None, None, None


def pull_program_data(
    session: Session, customer_id: int, stage: Stage
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    tables = ["coil_programs", "ah_programs", "program_ratings"]
    coil_prog_table, ah_prog_table, ratings = [
        ADP_DB.load_df(session=session, table_name=table, customer_id=customer_id)
        for table in tables
    ]
    match stage:
        case Stage.ACTIVE:
            active_coils = coil_prog_table["stage"] == stage.name
            active_ahs = ah_prog_table["stage"] == stage.name
            coil_prog_table = coil_prog_table[active_coils]
            ah_prog_table = ah_prog_table[active_ahs]
        case Stage.PROPOSED:
            active_coils = coil_prog_table["stage"] == Stage.ACTIVE.name
            active_ahs = ah_prog_table["stage"] == Stage.ACTIVE.name
            proposed_coils = coil_prog_table["stage"] == stage.name
            proposed_ahs = ah_prog_table["stage"] == stage.name
            coil_prog_table = coil_prog_table[(active_coils) | (proposed_coils)]
            ah_prog_table = ah_prog_table[(active_ahs) | (proposed_ahs)]
        case _:
            raise EmptyProgram

    return coil_prog_table, ah_prog_table, ratings


def generate_program(session: Session, customer_id: int, stage: Stage) -> ProgramFile:
    # TODO - swap out the underlying method to use v2 tables
    coil_prog_table, ah_prog_table, ratings = pull_program_data(
        session, customer_id, stage
    )
    try:
        coil_prog = build_coil_program(coil_prog_table, ratings)
        ah_prog = build_ah_program(ah_prog_table, ratings)
        full_program = add_customer_terms_parts_and_logo_path(
            session=session,
            customer_id=customer_id,
            coil_prog=coil_prog,
            ah_prog=ah_prog,
        )
        logger.info(f"generating {full_program}")
        for prog in full_program:
            logger.info(f"{prog} program included")
        price_book = (
            PriceBook(TEMPLATES, full_program)
            .build_program(session=session)
            .add_footer(offset=(0, 1))
            .attach_nomenclature_tab()
            .attach_ratings()
            .save_and_close()
        )
        new_program_file = ProgramFile(
            file_data=price_book, file_name=full_program.new_file_name()
        )
    except EmptyProgram:
        raise EmptyProgram("No program data to return")
    except Exception:
        import traceback as tb

        logger.info("Error occurred while trying to generate programs")
        logger.critical(tb.format_exc())
    else:
        # tables.remove("program_ratings")
        try:
            return new_program_file
            update_dates_in_tables(
                session=session, tables=tables, customer_id=customer_id
            )
        except Exception as e:
            logger.warning(
                "File Generation dates unable to be updated " f"due to an error: {e}"
            )
        return new_program_file


def update_dates_in_tables(
    session: Session, tables: Iterable[str], customer_id: int = None
) -> None:
    coil_update_q, ah_update_q = [
        f"""UPDATE {table}
            SET last_file_gen = :date
            WHERE customer_id 
            IN :customers;"""
        for table in tables
    ]
    params = {"customers": (customer_id,), "date": TODAY}
    with session:
        for q in coil_update_q, ah_update_q:
            ADP_DB.execute(session, q, params)
        session.commit()
