from dotenv import load_dotenv

load_dotenv()
import os
import pandas as pd
import logging
from time import time
from enum import Enum
from dataclasses import dataclass
from typing import Iterable
from datetime import datetime
from openpyxl.styles import Font, Alignment, numbers
from fastapi import HTTPException
from app.adp.adp_models import Fields
from app.adp.utils.programs import (
    CoilProgram,
    AirHandlerProgram,
    CustomerProgram,
    EmptyProgram,
)
from app.adp.utils.pricebook import PriceBook
from app.db import Session, ADP_DB, SCA_DB, Stage, DB_V2
from app.downloads import XLSXFileResponse


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


def fill_sort_order_field(df: pd.DataFrame) -> None:
    if "sort_order" not in df.columns:
        df["sort_order"] = 1
    elif df["sort_order"].isna().all():
        df["sort_order"] = 1
    elif df["sort_order"].isna().any():
        df["sort_order"].fillna(
            value=(df["sort_order"].dropna().astype(int).max() + 1),
            inplace=True,
        )
        df["sort_order"] = df["sort_order"].astype(int)
    else:
        df["sort_order"] = df["sort_order"].astype(int)
    return


def build_coil_program(
    program_data: pd.DataFrame, ratings: pd.DataFrame
) -> CoilProgram:
    prog_ratings = ratings.drop(columns=[Fields.CUSTOMER_ID.value])
    if program_data.empty:
        return CoilProgram(program_data=program_data, ratings=prog_ratings)
    program_data = program_data.drop(columns=["customer_id"])
    fill_sort_order_field(program_data)
    program_data = program_data.sort_values(
        by=[
            Fields.SORT_ORDER,
            Fields.CATEGORY.value,
            Fields.SERIES.value,
            Fields.METERING.value,
            Fields.TONNAGE.value,
            Fields.WIDTH.value,
            Fields.HEIGHT.value,
        ]
    ).drop_duplicates()
    return CoilProgram(program_data=program_data, ratings=prog_ratings)


def build_ah_program(
    program_data: pd.DataFrame, ratings: pd.DataFrame
) -> AirHandlerProgram:
    prog_ratings = ratings.drop(columns=[Fields.CUSTOMER_ID.value])
    if program_data.empty:
        return AirHandlerProgram(program_data=program_data, ratings=prog_ratings)
    program_data = program_data.drop(columns=["customer_id"])
    temp_heat_num_col = "heat_num"
    program_data[temp_heat_num_col] = (
        program_data[Fields.HEAT.value]
        .str.extract(r"(\d+|\d\.\d)\s*kW")
        .fillna(0)
        .astype(float)
        .astype(int)
    )
    fill_sort_order_field(program_data)
    program_data = program_data.sort_values(
        by=[
            Fields.SORT_ORDER,
            Fields.CATEGORY.value,
            Fields.SERIES.value,
            Fields.TONNAGE.value,
            Fields.WIDTH.value,
            temp_heat_num_col,
        ]
    ).drop_duplicates()
    program_data = program_data.drop(columns=[temp_heat_num_col])
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
    logger.info(f"customer_id: {customer_id}")
    customer_attrs_df = pd.DataFrame(
        customer_attrs.fetchall(), columns=customer_attrs.keys()
    )

    attr_ids = tuple(customer_attrs_df["attr_id"].to_list())
    attr_types_by_col = customer_attrs_df[["attr", "type"]]
    if attr_ids:
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
        try:
            customer_latest_effective_date = DB_V2.execute(
                session, sql_last_eff_date_by_customer, {"attr_ids": attr_ids}
            ).one()[-1]
        except Exception as e:
            logger.error(e)
            raise e
    else:
        customer_latest_effective_date = "1900-01-01"

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


def pull_customer_parts_v2(session: Session, customer_id: int) -> pd.DataFrame:
    """
    Tables:
        - vendor-customers (id)
        - vendor-products (vendor_product_identifier, vendor_product_description)
        - vendor-product-attrs (attr='pkg_qty')
        - vendor-pricing-by-customer (pricing class in 'PREFERRED_PARTS', 'STANDARD_PARTS')
        - vendor-pricing-by-customer-attrs (attr='sort_order')
    """
    sql = """
        SELECT vc.id AS customer_id,
            vp.vendor_product_identifier AS part_number,
            vp.vendor_product_description AS description,
            vpa.value AS pkg_qty,
            vpbc.price::float / 100 as preferred,
            vpbc.price::float / 100 as standard
        FROM vendor_customers vc
        JOIN vendor_pricing_by_customer vpbc ON vpbc.vendor_customer_id = vc.id
        JOIN vendor_products vp ON vp.id = vpbc.product_id
        JOIN vendor_product_attrs vpa ON vpa.vendor_product_id = vp.id
        LEFT JOIN vendor_pricing_by_customer_attrs vpca
            ON vpca.pricing_by_customer_id = vpbc.id and vpca.attr = 'sort_order'
        WHERE vc.id = :customer_id
        AND vpa.attr = 'pkg_qty'
        AND EXISTS (
            SELECT 1
            FROM vendor_pricing_classes vpc
            WHERE vpc.id = vpbc.pricing_class_id
            AND vpc.name IN ('PREFERRED_PARTS','STANDARD_PARTS')
            AND vpc.vendor_id = 'adp'
        )
        ORDER BY vpca.value::int;
    """
    try:
        result = DB_V2.execute(session, sql, {"customer_id": customer_id})
    except Exception as e:
        logger.error(f"parts_query failure: {e}")
        raise e
    else:
        return pd.DataFrame(result.fetchall(), columns=result.keys())


def pull_customer_aliases_v2(session: Session) -> pd.DataFrame:
    sql = """
        SELECT DISTINCT
            vc.id as id, 
            vc.name AS adp_alias,
            customers.name as customer,
            customers.id as sca_id, 
            vca.value::bool as preferred_parts
        FROM vendor_customers vc
        JOIN customer_location_mapping clm ON clm.vendor_customer_id = vc.id
        JOIN sca_customer_locations scl ON scl.id = clm.customer_location_id
        JOIN sca_customers customers ON customers.id = scl.customer_id
        JOIN vendor_customer_attrs vca ON vca.vendor_customer_id = vc.id
        WHERE vc.vendor_id = 'adp'
        AND vca.attr = 'preferred_parts';
    """
    result = DB_V2.execute(session, sql)
    return pd.DataFrame(result.fetchall(), columns=result.keys())


def pull_customer_parents_v2(session: Session) -> pd.DataFrame:
    return DB_V2.load_df(session=session, table_name="sca_customers")


def pull_customer_payment_terms(session: Session, customer_id: int) -> pd.DataFrame:

    try:
        result = pull_customer_payment_terms_v2(session, customer_id)
    except Exception as e:
        logger.warning(f"v2 payment terms method failed: {e}")
        raise e
    else:
        logger.info("Used V2 for customer payment terms")
        return result


def pull_customer_parts(session: Session, customer_id: int) -> pd.DataFrame:
    try:
        result = pull_customer_parts_v2(session, customer_id)
    except Exception as e:
        logger.warning(f"v2 parts method failed: {e}")
        raise e
    else:
        logger.info("Used V2 for customer program parts")
        return result


def pull_customer_alias_mapping(session: Session) -> pd.DataFrame:
    # NOTE while I could just write the query to pull the exact
    # record I need. I'm going to not do that for right now
    # because the method that uses this doesn't expect it
    try:
        result = pull_customer_aliases_v2(session)
    except Exception as e:
        logger.warning(f"v2 customer alias method failed: {e}")
        raise e
    else:
        logger.info("Used V2 for customer aliases")
    finally:
        return result


def pull_customer_parent_accounts(session: Session) -> pd.DataFrame:
    # NOTE while I could just write the query to pull the exact
    # record I need. I'm going to not do that for right now
    # because the method that uses this doesn't expect it
    try:
        result = pull_customer_parents_v2(session)
    except Exception as e:
        logger.warning(f"v2 customer parents method failed: {e}")
        result = SCA_DB.load_df(session=session, table_name="customers")
    else:
        logger.info("Used V2 for customer parents")
    finally:
        return result


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
    if not alias_mapping.empty:
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
    session: Session, customer_id: int, effective_date: datetime
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Pull together pricing by customer, the product info, and the customer-specific
    product info in order to reconstruct the ADP coils and Air Handlers schemas that
    used to be pulled directly from the database tables in V1.
    """

    if effective_date and effective_date > datetime.today():
        customer_strategy_sql = """
            SELECT 
                vpbc.id as price_id,
                vpbc.product_id,
                vpbc.vendor_customer_id as customer_id, 
                classes.name as cat_1,
                vp.vendor_product_identifier as model_number,
                vpbc_future.price
            FROM vendor_pricing_by_customer_future AS vpbc_future
            JOIN vendor_pricing_by_customer AS vpbc
                ON vpbc_future.price_id = vpbc.id
            JOIN vendor_products AS vp ON vp.id = vpbc.product_id
            JOIN vendor_product_to_class_mapping AS mapping ON mapping.product_id = vp.id
            JOIN vendor_product_classes AS classes ON classes.id = mapping.product_class_id
            WHERE vpbc.vendor_customer_id = :customer_id
            AND EXISTS (
                SELECT 1
                FROM vendor_pricing_classes AS vpc
                WHERE vpc.id = vpbc.pricing_class_id
                AND vpc.name = 'STRATEGY_PRICING'
                AND vp.vendor_id = 'adp'
            )
            AND classes.rank = 1
            AND vpbc.deleted_at IS NULL
            AND vpbc_future.effective_date <= :ed
        """
    else:
        customer_strategy_sql = """
            SELECT vpbc.id as price_id, vpbc.product_id, vpbc.vendor_customer_id as customer_id, 
                classes.name as cat_1, vp.vendor_product_identifier as model_number, vpbc.price
            FROM vendor_pricing_by_customer AS vpbc
            JOIN vendor_products AS vp ON vp.id = vpbc.product_id
            JOIN vendor_product_to_class_mapping AS mapping ON mapping.product_id = vp.id
            JOIN vendor_product_classes AS classes ON classes.id = mapping.product_class_id
            WHERE vpbc.vendor_customer_id = :customer_id
            AND EXISTS (
                SELECT 1
                FROM vendor_pricing_classes AS vpc
                WHERE vpc.id = vpbc.pricing_class_id
                AND vpc.name = 'STRATEGY_PRICING'
                AND vp.vendor_id = 'adp'
            )
            AND classes.rank = 1
            AND vpbc.deleted_at IS NULL;
        """
    strategy_product_custom_desc_sql = """
        SELECT pricing_by_customer_id as price_id, value as "category"
        FROM vendor_pricing_by_customer_attrs
        WHERE pricing_by_customer_id IN :ids
        AND attr = 'custom_description'; 
    """
    strategy_product_custom_feature_sql = """
        SELECT pricing_by_customer_id as price_id, attr, value
        FROM vendor_pricing_by_customer_attrs
        WHERE pricing_by_customer_id IN :ids
        AND attr IN (
            'private_label',
            'ratings_ac_txv',
            'ratings_hp_txv',
            'ratings_field_txv',
            'ratings_piston',
            'sort_order'
        ); 
    """
    strategy_product_attrs = """
        SELECT vendor_product_id AS product_id, attr, value
        FROM vendor_product_attrs
        WHERE vendor_product_id IN :product_ids
        AND attr NOT IN ('category','private_label');
    """
    customer_strategy = pd.DataFrame(
        DB_V2.execute(
            session,
            customer_strategy_sql,
            dict(customer_id=customer_id, ed=effective_date),
        )
        .mappings()
        .fetchall()
    )
    if customer_strategy.empty:
        raise EmptyProgram("No customer strategy exists")
    strategy_product_desc = pd.DataFrame(
        DB_V2.execute(
            session,
            strategy_product_custom_desc_sql,
            dict(ids=tuple(customer_strategy["price_id"].tolist())),
        )
        .mappings()
        .fetchall()
    )
    strategy_custom_features = pd.DataFrame(
        DB_V2.execute(
            session,
            strategy_product_custom_feature_sql,
            dict(ids=tuple(customer_strategy["price_id"].tolist())),
        )
        .mappings()
        .fetchall()
    )
    strategy_product_attrs = pd.DataFrame(
        DB_V2.execute(
            session,
            strategy_product_attrs,
            dict(product_ids=tuple(customer_strategy["product_id"].unique().tolist())),
        )
        .mappings()
        .fetchall()
    )
    strat_prod_pivoted = strategy_product_attrs.pivot(
        index="product_id", columns="attr", values="value"
    )
    customer_strategy_detailed = (
        customer_strategy.merge(strategy_product_desc, on="price_id", how="outer")
        .merge(strat_prod_pivoted, on="product_id")
        .rename(columns={"price": "net_price"})
    )
    if not strategy_custom_features.empty:
        # merge in private label data and swap out values for ratings comparisons
        # with private label-specific ratings patterns
        strategy_custom_features = strategy_custom_features.pivot(
            index="price_id", columns="attr"
        )
        col_list: list[str] = strategy_custom_features.columns.get_level_values(
            1
        ).to_list()
        strategy_custom_features.columns = [
            col.replace("ratings", "pl_ratings") for col in col_list
        ]
        strategy_custom_features = strategy_custom_features.reset_index()
        customer_strategy_detailed = customer_strategy_detailed.merge(
            strategy_custom_features, on="price_id", how="outer"
        )
        pl_ratings_cols: list[str] = customer_strategy_detailed.columns[
            customer_strategy_detailed.columns.str.startswith("pl_ratings")
        ].to_list()
        for col in pl_ratings_cols:
            target = col.replace("pl_", "")
            mask = ~customer_strategy_detailed[col].isna()
            customer_strategy_detailed.loc[mask, target] = (
                customer_strategy_detailed.loc[mask, col]
            )
        customer_strategy_detailed.drop(columns=pl_ratings_cols, inplace=True)

    customer_strategy_detailed["stage"] = "ACTIVE"
    customer_strategy_detailed["net_price"] /= 100

    coils = customer_strategy_detailed[
        customer_strategy_detailed["cat_1"] == "Coils"
    ].dropna(how="all", axis=1)
    if Fields.PRIVATE_LABEL.value not in coils.columns:
        coils[Fields.PRIVATE_LABEL.value] = None
    num_cols = {
        "width": float,
        "depth": float,
        "height": float,
        "length": float,
        "depth": float,
        "weight": int,
        "pallet_qty": int,
        "min_qty": int,
        "sort_order": int,
    }
    try:
        num_cols_trimmed = {n: t for n, t in num_cols.items() if n in coils.columns}
        coils = coils.astype(num_cols_trimmed, errors="ignore")
    except Exception as e:
        logger.info(f"Unable to convert num cols: {e}")

    ahs = customer_strategy_detailed[
        customer_strategy_detailed["cat_1"] == "Air Handlers"
    ].dropna(how="all", axis=1)
    if Fields.PRIVATE_LABEL.value not in ahs.columns:
        ahs[Fields.PRIVATE_LABEL.value] = None
    try:
        num_cols_trimmed = {n: t for n, t in num_cols.items() if n in ahs.columns}
        ahs = ahs.astype(num_cols_trimmed, errors="ignore")
    except Exception as e:
        logger.info(f"Unable to convert num cols: {e}")
    ratings = DB_V2.load_df(session, "adp_program_ratings", customer_id)
    return coils, ahs, ratings


def pull_program_data(
    session: Session, customer_id: int, effective_date: datetime
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    try:
        result = pull_program_data_v2(session, customer_id, effective_date)
    except Exception as e:
        logger.warning(f"v2 product data method failed")
        raise e
    else:
        logger.info("Used V2 for customer program products")
        return result


def generate_program(
    session: Session, customer_id: int, effective_date: datetime
) -> XLSXFileResponse:
    start = time()
    try:
        coil_prog_table, ah_prog_table, ratings = pull_program_data(
            session, customer_id, effective_date
        )
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
            file_data=price_book, file_name=full_program.new_file_name(effective_date)
        )
    except EmptyProgram:
        raise HTTPException(status_code=404, detail="No program data to return")
    except Exception as e:
        import traceback as tb

        trace = tb.format_exc()
        logger.error("Error occurred while trying to generate programs")
        raise HTTPException(status_code=404, detail="No program data to return")
    else:
        logger.info(f"transform time: {time()-start}")
        return XLSXFileResponse(
            content=new_program_file.file_data, filename=new_program_file.file_name
        )
    finally:
        session.close()


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
