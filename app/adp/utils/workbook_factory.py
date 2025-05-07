from dotenv import load_dotenv

load_dotenv()
import os
import pandas as pd
import logging
from time import time
from datetime import datetime
from openpyxl.styles import Font, Alignment, numbers
from fastapi import HTTPException
from app.adp.adp_models import Fields
from app.adp.utils.models import AttrType, ProgramFile
from app.adp.utils.programs import (
    CoilProgram,
    AirHandlerProgram,
    MfurnaceProgram,
    CustomerProgram,
    EmptyProgram,
)
from app.adp.utils.pricebook import PriceBook
from app.db import Session, DB_V2
from app.db.sql import queries
from app.downloads import XLSXFileResponse


logger = logging.getLogger("uvicorn.info")
TODAY = str(datetime.today().date())
TEMPLATES = os.getenv("TEMPLATES")


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


def build_furnace_program(
    program_data: pd.DataFrame, ratings: pd.DataFrame
) -> MfurnaceProgram:
    prog_ratings = ratings.drop(columns=[Fields.CUSTOMER_ID.value])
    if program_data.empty:
        return MfurnaceProgram(program_data=program_data, ratings=prog_ratings)
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
    return MfurnaceProgram(program_data=program_data, ratings=prog_ratings)


def pull_customer_payment_terms_v2(session: Session, customer_id: int) -> pd.DataFrame:
    sql_attrs = queries.adp_customer_attributes
    customer_attrs = DB_V2.execute(session, sql_attrs, {"customer_id": customer_id})
    logger.info(f"customer_id: {customer_id}")
    customer_attrs_df = pd.DataFrame(
        customer_attrs.fetchall(), columns=customer_attrs.keys()
    )

    attr_types_by_col = customer_attrs_df[["attr", "type"]]
    customer_latest_effective_date = datetime.today().date()

    # ought to be a one-row table now
    customer_attrs_df = customer_attrs_df.pivot(
        index="customer_id", columns="attr", values="value"
    )
    customer_attrs_df["effective_date"] = str(customer_latest_effective_date)
    for attr in attr_types_by_col.itertuples():
        customer_attrs_df[attr.attr] = customer_attrs_df[attr.attr].astype(
            AttrType[attr.type].value
        )

    customer_attrs_df = customer_attrs_df.infer_objects()
    return customer_attrs_df


def pull_customer_parts_v2(
    session: Session, customer_id: int, effective_date: datetime
) -> pd.DataFrame:
    sql = queries.adp_customer_parts
    try:
        params = dict(
            customer_id=customer_id,
            ed=effective_date if effective_date else datetime.today(),
        )
        result = DB_V2.execute(session, sql, params)
    except Exception as e:
        logger.error(f"parts_query failure: {e}")
        raise e
    else:
        return pd.DataFrame(result.fetchall(), columns=result.keys())


def pull_customer_aliases_v2(session: Session) -> pd.DataFrame:
    sql = queries.adp_customer_aliases
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


def pull_customer_parts(
    session: Session, customer_id: int, effective_date: datetime
) -> pd.DataFrame:
    try:
        result = pull_customer_parts_v2(session, customer_id, effective_date)
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
        result = DB_V2.load_df(session=session, table_name="sca_customers")
    else:
        logger.info("Used V2 for customer parents")
    finally:
        return result


def add_customer_terms_parts_and_logo_path(
    session: Session,
    customer_id: int,
    coil_prog: CoilProgram,
    ah_prog: AirHandlerProgram,
    furnace_prog: MfurnaceProgram,
    effective_date: datetime | None,
) -> CustomerProgram:

    footer = pull_customer_payment_terms(session, customer_id)
    prog_parts = pull_customer_parts(session, customer_id, effective_date)
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
        if effective_date:
            effective_date = str(effective_date)
        else:
            effective_date = str(footer["effective_date"].item())
    except:
        logger.info(f"footer capture failed for {alias_name}")
        payment_terms = None
        pre_paid_freight = None
        effective_date = "1900-01-01 00:00:00"
    try:
        parsed_date = datetime.strptime(effective_date, r"%Y-%m-%d %H:%M:%S")
    except ValueError:
        parsed_date = datetime.strptime(effective_date, r"%Y-%m-%d")
    except Exception as e:
        logger.error(f"Invalid effective_date format: {effective_date}")
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
            "value": parsed_date,
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
        furnaces=furnace_prog,
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
        use_future = True
    else:
        use_future = False

    strategy_product_custom_desc_sql = queries.adp_strategy_custom_descriptions
    strategy_product_custom_feature_sql = queries.adp_strategy_custom_features
    strategy_product_attrs = queries.adp_strategy_product_attributes
    customer_strategy_sql = queries.adp_customer_strategy_data
    customer_strategy = pd.DataFrame(
        DB_V2.execute(
            session,
            customer_strategy_sql,
            dict(customer_id=customer_id, ed=effective_date, use_future=use_future),
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
    session: Session, customer_id: int, effective_date: datetime | None
) -> XLSXFileResponse:
    start = time()
    try:
        coil_prog_table, ah_prog_table, ratings = pull_program_data(
            session, customer_id, effective_date
        )
        amh_ah_mask = ah_prog_table[Fields.MODEL_NUMBER].str.startswith("AMH")
        coil_prog = build_coil_program(coil_prog_table, ratings)
        ah_prog = build_ah_program(ah_prog_table[~amh_ah_mask], ratings)
        furn_prog = build_furnace_program(ah_prog_table[amh_ah_mask], ratings)
        full_program = add_customer_terms_parts_and_logo_path(
            session=session,
            customer_id=customer_id,
            coil_prog=coil_prog,
            ah_prog=ah_prog,
            furnace_prog=furn_prog,
            effective_date=effective_date,
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
        logger.info(trace)
        raise HTTPException(status_code=404, detail="No program data to return")
    else:
        logger.info(f"transform time: {time()-start}")
        return XLSXFileResponse(
            content=new_program_file.file_data, filename=new_program_file.file_name
        )
    finally:
        session.close()
