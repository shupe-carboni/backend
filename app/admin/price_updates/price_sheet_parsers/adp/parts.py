from datetime import datetime
from logging import getLogger
from pandas import DataFrame, to_numeric
from numpy import nan
from app.db.sql import queries as SQL
from app.db import Session, DB_V2

logger = getLogger("uvicorn.info")


def adp_parts_sheet_parser(
    session: Session, df: DataFrame, effective_date: datetime, *args, **kwargs
) -> None:
    df = df.iloc[4:, :5]
    df.columns = [
        "part_number",
        "description",
        "pkg_qty",
        "preferred",
        "standard",
    ]
    df.loc[:, "preferred"] = to_numeric(df["preferred"], errors="coerce") * 100
    df.loc[:, "standard"] = to_numeric(df["standard"], errors="coerce") * 100
    df.dropna(subset="part_number", inplace=True)
    df.replace({nan: None}, inplace=True)
    df_records = df.to_dict(orient="records")

    setup_ = SQL.adp_parts_temp_table
    populate_parts_temp = SQL.adp_parts_populate_temp
    insert_new_parts = SQL.adp_parts_insert_new_product
    # expecting returned ids from prior insert for next queries
    define_pkg_qtys_for_new_parts = SQL.adp_parts_setup_attrs_new_product
    insert_new_prices = SQL.adp_parts_new_product_pricing
    establish_future_pricing = SQL.adp_parts_establish_future
    eff_date_param = dict(ed=effective_date)

    session.begin()
    try:
        DB_V2.execute(session, setup_)
        DB_V2.execute(session, populate_parts_temp, df_records)
        new_ids = tuple(
            [rec[0] for rec in DB_V2.execute(session, insert_new_parts).fetchall()]
        )
        if new_ids:
            new_ids_param = dict(new_part_ids=new_ids)
            DB_V2.execute(session, define_pkg_qtys_for_new_parts, new_ids_param)
            DB_V2.execute(
                session,
                insert_new_prices,
                new_ids_param | eff_date_param,
            )
        DB_V2.execute(session, establish_future_pricing, eff_date_param)
    except Exception as e:
        import traceback as tb

        logger.error(tb.format_exc())
        session.rollback()
    else:
        session.commit()
    finally:
        session.close()
