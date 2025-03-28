from datetime import datetime
from logging import getLogger
from pandas import DataFrame, concat
from fastapi import HTTPException, status, BackgroundTasks

import app.db.sql as SQL
from app.db.sql import queries
from app.db import Session, DB_V2
from app.admin.models import (
    ADPProductSheet,
    ADPCustomerRefSheet,
    ADPProductType,
    ProductType,
    VendorId,
)
import app.admin.price_updates.price_sheet_parsers as parsers

from app.adp.extraction.models import parse_model_string, ParsingModes

logger = getLogger("uvicorn.info")

## Percentage Increases


def apply_percentage(
    session: Session,
    vendor_id: VendorId,
    increase_pct: float | int,
    effective_date: datetime,
) -> None:
    """
    Take the percentage amount and apply it to all records
    in vendor-pricing-by-customer and vendor-pricing-by-class

    Discounts are not expected to change, just the underlying price points.
    """
    class_pricing_update = queries.apply_percentage_on_class_price
    customer_pricing_update = queries.apply_percentage_on_customer_price
    # assume percentage is in the form like 0.055, not 5.5
    if increase_pct > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Percentage increase is over 100%: {increase_pct*100:0.2f}%",
        )
    multiplier = 1 + increase_pct
    params = dict(multiplier=multiplier, ed=effective_date, vendor_id=vendor_id.value)
    session.begin()
    try:
        DB_V2.execute(session, class_pricing_update, params)
        DB_V2.execute(session, customer_pricing_update, params)
    except Exception as e:
        logger.critical(e)
        session.rollback()
    else:
        logger.info(
            "Future Pricing established with an increase percentage of "
            f"{increase_pct*100:0.2f}%"
        )
        session.commit()
    finally:
        session.close()


## ATCO
def atco_price_update(
    session: Session, dfs: dict[str, DataFrame], effective_date: datetime
):
    """One file with a sheet for each region (a vendor-pricing-class).
    Aligning with states or parts of states. Customers are assigned to one
    or more class, and some customers have special pricing on classes of products
    represented as multipliers. This method expects a list price change (repeated
    on each sheet) and potentially multiplier changes.
    Each sheet has a listing of products, almost identical but not completely.
    Each sheet has multipliers that correspond to the state-region (vendor-pricing-class)
    and product category (vendor-product-class, rank 1).

    TODO: CIRCLE BACK WITH ERROR HANDLING
    """
    sheet_name_conversion = {
        "Alabama": "AL",
        "Florida": "FL",
        "Georgia": "GA",
        "KYINOH": "KY",
        "MS": "MS (MS/W-TN)",
        "Tennessee": "TN (MIDDLE & EAST)",
    }
    dfs = {sheet_name_conversion.get(sn, sn): df for sn, df in dfs.items()}

    multiplier_dfs = []
    pricing_dfs = []
    # Split pricing and multipliers
    # manipulate the index of multipliers in order to fill
    # the product class name in for pricing
    # which will be needed to map new products to classes
    for sheet, df in dfs.items():
        multiplier_df = df.iloc[5:, :4]
        multiplier_df = (
            multiplier_df[multiplier_df.iloc[:, -1].isna()].iloc[:, [0, 2]].dropna()
        )
        multiplier_df.columns = ["product_class_name", "multiplier"]
        multiplier_df["pricing_class_name"] = sheet
        multiplier_df.index = multiplier_df.index + 1
        multiplier_dfs.append(multiplier_df)

        pricing_df = df.iloc[6:, [0, 1, 3, 12]]
        pricing_df = pricing_df[
            ~(pricing_df.iloc[:, 2].isna())
            & ~(pricing_df.iloc[:, 2] == "Type Description")
        ].iloc[:, [0, 1, 3]]
        pricing_df["product_category_name"] = multiplier_df["product_class_name"]
        pricing_df.loc[:, "product_category_name"] = pricing_df[
            "product_category_name"
        ].ffill()
        pricing_df.columns = [
            "part_number",
            "description",
            "price",
            "product_category_name",
        ]
        pricing_df["price"] *= 100
        pricing_df["price"] = pricing_df["price"].astype(int)
        pricing_dfs.append(pricing_df)

    multipliers = concat(multiplier_dfs)
    m_records: list[dict] = multipliers.to_dict("records")
    logger.info("New multiplier records created")

    pricing = concat(pricing_dfs).drop_duplicates()
    p_records: list[dict] = pricing.to_dict("records")
    logger.info("New pricing records created")

    temp_table_multipliers = SQL.queries.atco_mults_temp_setup
    insert_multipliers = SQL.queries.atco_mults_pop_temp
    temp_table_pricing = SQL.queries.atco_pricing_temp_setup
    insert_pricing = SQL.queries.atco_pricing_pop_temp
    atco_price_updates_sql = SQL.queries.atco_price_updates
    try:
        logger.info("setting up temp tables")
        DB_V2.execute(session, temp_table_multipliers)
        DB_V2.execute(session, temp_table_pricing)
        DB_V2.execute(session, insert_multipliers, m_records)
        DB_V2.execute(session, insert_pricing, p_records)
        date_param = dict(ed=str(effective_date))
        DB_V2.execute(session, atco_price_updates_sql, params=date_param)
        logger.info("Price update successful")
    except Exception as e:
        logger.info("An error occured while trying to update pricing")
        logger.error(e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return 200
    finally:
        drop_ = SQL.queries.atco_teardown
        DB_V2.execute(session, drop_)


## ADP
async def _adp_update_zero_disc_prices(
    session: Session, effective_date: datetime, coils: bool, air_handlers: bool
) -> None:
    logger.info("Background update process begun")
    match coils, air_handlers:
        case True, True:
            prod_cats = ("Coils", "Air Handlers")
        case False, True:
            prod_cats = ("Air Handlers",)
        case True, False:
            prod_cats = ("Coils",)
        case False, False:
            return
    try:
        logger.info("Retrieving all Zero Discount products with price ids")
        all_models_sql = SQL.queries.adp_zero_disc_get_all_models
        all_models = DB_V2.execute(
            session,
            all_models_sql,
            dict(product_categories=prod_cats),
        ).fetchall()
        logger.info(f"Repricing {len(all_models)} models ...")
        new_pricing_by_id = []
        for i, rec in enumerate(all_models):
            id_, model = rec
            logger.info(f"    {model} ({i+1} of {len(all_models)})")
            try:
                fresh_build = parse_model_string(
                    session, 0, model, ParsingModes.BASE_PRICE_FUTURE
                )
            except Exception as e:
                logger.error(f"   failed to price {model}: {e}")
                continue
            else:
                repriced = (id_, fresh_build["zero_discount_price"] * 100)
                new_pricing_by_id.append(repriced)
        new_pricing_params = [
            {"id": id_, "price": price} for id_, price in new_pricing_by_id
        ]
        logger.info("Finished calculations")
        update_setup = SQL.queries.adp_zero_disc_setup
        populate_update = SQL.queries.adp_zero_disc_pop_temp
        establish_future_pricing = SQL.queries.adp_zero_disc_establish_future
        try:
            DB_V2.execute(session, update_setup)
            DB_V2.execute(session, populate_update, new_pricing_params)
            logger.info("temp table setup")
            DB_V2.execute(session, establish_future_pricing, dict(ed=effective_date))
            DB_V2.execute(session, "DROP TABLE IF EXISTS adp_zd;")
        except Exception as e:
            session.rollback()
            import traceback as tb

            logger.critical("Update failed")
            logger.critical(tb.format_exc())
        else:
            session.commit()
            logger.info("Update Successful")
    finally:
        session.close()


async def _adp_update_customer_prices(
    session: Session, effective_date: datetime
) -> None:
    logger.info("Background Update Process begun")
    all_models_sql = SQL.queries.adp_customer_pricing_all_models
    try:
        logger.info("Retriving all customer pricing ...")
        all_models = DB_V2.execute(session, all_models_sql).fetchall()
        logger.info(f"Repricing {len(all_models)} models ...")

        new_pricing_by_id = []
        for i, rec in enumerate(all_models):
            id_, model, customer_id, private_label = rec
            if private_label:
                model = private_label
            logger.info(
                f"customer:{customer_id} - {model} ({i+1} of {len(all_models)})"
            )
            try:
                fresh_build = parse_model_string(
                    session, customer_id, model, ParsingModes.CUSTOMER_PRICING_FUTURE
                )
            except Exception as e:
                logger.error(f"   failed to price {model}")
                continue
            else:
                repriced = (id_, fresh_build["net_price"] * 100)
                new_pricing_by_id.append(repriced)

        new_pricing_params = [
            {"id": id_, "price": price} for id_, price in new_pricing_by_id
        ]
        logger.info("Finished calculations")
        update_setup = SQL.queries.adp_customer_pricing_temp_setup
        populate_update = SQL.queries.adp_customer_pricing_pop_temp
        establish_future_pricing = SQL.queries.adp_customer_pricing_establish_future
        try:
            DB_V2.execute(session, update_setup)
            DB_V2.execute(session, populate_update, new_pricing_params)
            logger.info("temp table setup")
            DB_V2.execute(session, establish_future_pricing, dict(ed=effective_date))
            logger.info("tearing down")
            DB_V2.execute(session, SQL.queries.adp_customer_pricing_teardown)
        except Exception as e:
            session.rollback()
            import traceback as tb

            logger.critical("Update failed")
            logger.critical(tb.format_exc())
        else:
            session.commit()
            logger.info("Update Successful")
    finally:
        session.close()


def _adp_price_sheet_parsing_and_key_price_establishment(
    session: Session,
    sheets: dict[ADPCustomerRefSheet, DataFrame],
    effective_date: datetime,
    bg: BackgroundTasks,
) -> int:
    coils = False
    air_handlers = False
    parser_map = {
        ADPProductSheet.B: parsers.adp_b_series_sheet,
        ADPProductSheet.CP_A1: parsers.adp_cp_series_sheet,
        ADPProductSheet.CP_A2L: parsers.adp_cp_series_sheet,
        ADPProductSheet.F: parsers.adp_f_series_sheet,
        ADPProductSheet.S: parsers.adp_s_series_sheet,
        ADPProductSheet.AMH: parsers.adp_amh_series_sheet,
        ADPProductSheet.HE: parsers.adp_he_series_sheet,
        ADPProductSheet.HH: parsers.adp_hh_series_sheet,
        ADPProductSheet.MH: parsers.adp_mh_series_sheet,
        ADPProductSheet.V: parsers.adp_v_series_sheet,
        ADPProductSheet.HD: parsers.adp_hd_series_sheet,
        ADPProductSheet.SC: parsers.adp_sc_series_sheet,
    }
    results = []
    for series, df in sheets.items():
        if series == ADPProductSheet.PARTS:
            # direct parsing
            parsers.adp_parts_sheet(session, df, effective_date)
            continue
        match ADPProductType[series.name].value:
            case ProductType.COILS if not coils:
                coils = True
            case ProductType.AIR_HANDLERS if not air_handlers:
                air_handlers = True
        logger.info(f"processing sheet: {series}")
        results.extend([*parser_map[series](df, series)])

    all_keys = concat(results, ignore_index=True)
    all_keys.loc[:, "effective_date"] = effective_date

    setup_ = SQL.queries.adp_product_series_temp_table
    additional_setup = SQL.queries.adp_product_series_pop_temp
    establish_future_key_prices = SQL.queries.adp_product_series_establish_future
    teardown = SQL.queries.adp_product_series_teardown

    records = all_keys.dropna().to_dict(orient="records")
    logger.info("updating records")
    session.begin()
    try:
        DB_V2.execute(session, setup_)
        DB_V2.execute(session, additional_setup, params=records)
        DB_V2.execute(session, establish_future_key_prices)
        logger.info("tearing down")
        DB_V2.execute(session, teardown)
    except Exception as e:
        logger.critical(e)
        session.rollback()
        raise HTTPException(status_code=500, detail=e)
    else:
        bg.add_task(
            _adp_update_zero_disc_prices,
            session=session,
            effective_date=effective_date,
            coils=coils,
            air_handlers=air_handlers,
        )
        return 202


def _adp_master_parsing_and_customer_price_updates(
    session: Session,
    sheets: dict[ADPCustomerRefSheet, DataFrame],
    effective_date: datetime,
    bg: BackgroundTasks,
) -> int:
    for sheet, df in sheets.items():
        setup_new_customers = SQL.queries.adp_customers_tamp_table
        populate_new_customers = SQL.queries.adp_customers_pop_temp
        add_new_customers = SQL.queries.adp_customers_insert_new
        teardown = SQL.queries.adp_customers_temp_teardown
        clear_ = teardown
        logger.info(f"processing sheet: {sheet}")
        match sheet:
            case ADPCustomerRefSheet.CUSTOMER_DISCOUNT:
                df = df[["Customer Name", "Material", "Price"]]
                df.columns = ["customer", "mg", "discount"]
                df_records = df.to_dict(orient="records")
                customers = df["customer"].str.strip().unique()
                customer_records = [{"customer": c} for c in customers.tolist()]
                # ADPs discounts are provided in 0.01-base
                # ADPs discounts are stored in 0.01-base
                # df["discount"] /= 100
                setup_mg_update = SQL.queries.adp_discounts_temp_table
                populate_mg_update = SQL.queries.adp_discounts_populate_temp
                update_discounts = SQL.queries.adp_discounts_establish_future
                add_new_customer_discounts = SQL.queries.adp_discounts_insert_new

                session.begin()
                eff_date_param = dict(ed=effective_date)
                try:
                    DB_V2.execute(session, clear_)
                    DB_V2.execute(session, setup_new_customers)
                    DB_V2.execute(
                        session,
                        populate_new_customers,
                        params=customer_records,
                    )
                    DB_V2.execute(session, add_new_customers)
                    DB_V2.execute(session, setup_mg_update)
                    DB_V2.execute(session, populate_mg_update, params=df_records)
                    DB_V2.execute(
                        session,
                        update_discounts,
                        params=eff_date_param,
                    )
                    DB_V2.execute(
                        session,
                        add_new_customer_discounts,
                        params=eff_date_param,
                    )
                    DB_V2.execute(session, teardown)
                except Exception as e:
                    import traceback as tb

                    print(tb.format_exc())
                    session.rollback()
                else:
                    logger.info(f"update succesful")
                    session.commit()

            case ADPCustomerRefSheet.SPECIAL_NET:
                df = df[["Customer Name", "Material", "Material Description", "Price"]]
                df.columns = ["customer", "part_id", "description", "price"]
                df.loc[:, "description"] = (
                    df["description"].str.split("  ", n=1, expand=True)[0].str.strip()
                )
                # air handlers my have wrong model numbers (no trailing "A" on A1)
                ah_prefixes = {"SM", "SK", "SL", "FE", "FC", "CP"}
                mask = (df["description"].str.startswith(tuple(ah_prefixes))) & ~(
                    df["description"].str.endswith(("A", "R"))
                )
                df.loc[mask, "description"] += "A"
                mask = df["description"].str.contains("RDS KIT")
                df.loc[mask, "description"] = df.loc[mask, "part_id"]
                df.drop(columns="part_id", inplace=True)
                df["price"] *= 100
                df_records = df.to_dict(orient="records")
                eff_date_param = dict(ed=effective_date)

                setup_snp_update = SQL.queries.adp_snps_temp_table
                populate_snp_update = SQL.queries.adp_snps_pop_temp
                # TODO figure out how to incorporate private labels
                add_new_snps = SQL.queries.adp_snps_insert_new
                update_snps = SQL.queries.adp_snps_establish_future
                teardown = SQL.queries.adp_snps_teardown
                logger.info("updating SNPs")
                session.begin()
                try:
                    DB_V2.execute(session, setup_snp_update)
                    DB_V2.execute(session, populate_snp_update, params=df_records)
                    DB_V2.execute(session, update_snps, params=eff_date_param)
                    DB_V2.execute(session, add_new_snps, params=eff_date_param)
                    DB_V2.execute(session, teardown)
                except Exception as e:
                    import traceback as tb

                    print(tb.format_exc())
                    session.rollback()
                else:
                    logger.info(f"update succesful")
                    session.commit()

            case ADPCustomerRefSheet.ZERO_DISCOUNT:
                logger.info(f"skipped")
                continue
            case ADPCustomerRefSheet.COMBINED:
                logger.info(f"skipped")
                continue
            case ADPCustomerRefSheet.OO:
                logger.info(f"skipped")
                continue

    # perform update on customer strategies
    bg.add_task(
        _adp_update_customer_prices,
        session=session,
        effective_date=effective_date,
    )
    return 202


def adp_price_update(
    session: Session,
    dfs: dict[str, DataFrame],
    effective_date: datetime,
    bg: BackgroundTasks,
):
    """
    ADP keeps separate files for air handlers and coils. This method will handle either
    one, but ultimately two requests will be needed to complete a full update on
    products PLUS an additional request just for parts/accessories.

    Each file will have stylized pricing that needs to be formatted for updates to
    *vendor_product_series_pricing*. This table schema has product Series

    BUG I have a race condition such that if I put the repricing of ZERO_DISCOUNT
        in the background, a new request with customer SNPs and Mat Grp Discounts
        could come in before that's finished
    """

    product_pricing_sheets = {
        ADPProductSheet(sn): df
        for sn, df in dfs.items()
        if sn in ADPProductSheet.__members__.values()
    }
    customer_reference_sheets = {
        ADPCustomerRefSheet(sn): df
        for sn, df in dfs.items()
        if sn in ADPCustomerRefSheet.__members__.values()
    }
    both_ = product_pricing_sheets and customer_reference_sheets
    either_ = product_pricing_sheets or customer_reference_sheets
    if both_ or not either_:
        raise Exception(
            "Expecting either product references or customer references."
            " Upload either the Coil Price Book, the AH price book, or the "
            "Master Price file."
        )
    elif product_pricing_sheets:
        _adp_price_sheet_parsing_and_key_price_establishment(
            session, product_pricing_sheets, effective_date, bg
        )
    else:
        _adp_master_parsing_and_customer_price_updates(
            session, customer_reference_sheets, effective_date, bg
        )
