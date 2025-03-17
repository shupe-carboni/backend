import os
import logging
from datetime import datetime
from typing import Annotated
from fastapi import (
    HTTPException,
    Depends,
    UploadFile,
    status,
    Response,
    BackgroundTasks,
)
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app import auth
from app.db import DB_V2
from app.adp.extraction.models import parse_model_string, ParsingModes
from numpy import nan
from pandas import read_csv, ExcelFile, DataFrame, concat, Series, to_numeric
from app.admin.models import VendorId
from app.admin.models import ADPProductSheet, ADPCustomerRefSheet, DBOps
from app.admin.price_update_sql import SQL


price_updates = APIRouter(prefix=f"/admin/price-updates", tags=["admin"])
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]
logger = logging.getLogger("uvicorn.info")


@price_updates.post("/{vendor_id}")
async def new_pricing(
    session: NewSession,
    token: Token,
    vendor_id: VendorId,
    file: UploadFile,
    effective_date: datetime,
    bg: BackgroundTasks,
) -> None:
    """Take files as-is, assuming only one file, and parse it for a whole-catalog
    pricing update.

    The following method is highly coupled to vendor file structure & pricing structure,
    and while used infrequently, it is designed for powerfully large updates to business
    critical price information. It may break due to small tweaks to file structure or
    unexpected pricing behavior.

    Firstly, only an SCA admin may execute this method.
    The file is read, and the data, either in the form of a CSV or an Excel file,
    will be routed to a vendor-specific method based on the vendor_id passed into the
    route.

    Good Luck.
    """
    logger.info("Price Update request recieved")
    if token.permissions < auth.Permissions.sca_admin:
        logger.info("Insufficient permissions. Rejected.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    file_data = await file.read()
    match file.content_type:
        case "text/csv":
            file_df = read_csv(file_data).replace({nan: None})
        case "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            with ExcelFile(file_data) as excel_file:
                file_df_collection = {
                    sheet.title.strip(): excel_file.parse(
                        sheet.title, data_only=True
                    ).replace({nan: None})
                    for sheet in excel_file.book.worksheets
                    if sheet.sheet_state == "visible"
                }
        case _:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    logger.info(f"File read sucessfully - Routing to {vendor_id}")
    match vendor_id:
        case VendorId.ATCO:
            atco_price_update(session, file_df_collection, effective_date)
        case VendorId.ADP:
            adp_price_update(session, file_df_collection, effective_date, bg)
        case VendorId.BERRY:
            ...
        case VendorId.FRIEDRICH:
            ...
        case VendorId.GLASFLOSS:
            ...
        case VendorId.MILWAUKEE:
            ...
        case _:
            logger.info(f"vendor {vendor_id} unable to be routed")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return Response(status_code=status.HTTP_200_OK)


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

    - Convert sheet names to valid pricing class names.
    - Extract multipliers for each product class by price class (sheet).
    - Extract all data for pricing, trimmed down and treated.
    - Add any new product that isn't currently in the products table
    - Update LIST_PRICE by joining against Part #
    - Insert new LIST_PRICE by an exclusive join against Part #
    - Update all other class prices joining LIST_PRICE records against product classes
        and multiplying by the multiplier.
    - Update vendor-pricing-by-customer by joining LIST_PRICE against
        vendor-product-class-discounts (assuming here that these were not changed as
        part of the pricing adjustment) and product classes.

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

    temp_table_multipliers = """
    -- load in new data
        CREATE TEMPORARY TABLE atco_multipliers (
            product_class_name varchar,
            multiplier float,
            pricing_class_name varchar
        );
    """
    insert_multipliers = """
        INSERT INTO atco_multipliers
        VALUES (:product_class_name, :multiplier, :pricing_class_name);
    """
    temp_table_pricing = """
        CREATE TEMPORARY TABLE atco_pricing (
            part_number varchar,
            description varchar,
            price int,
            product_category_name varchar
        );
    """
    insert_pricing = """
        INSERT INTO atco_pricing
        VALUES (:part_number, :description, :price, :product_category_name);
    """
    sql_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "atco_price_updates.sql"
    )
    with open(sql_file) as fh:
        logger.info("Importing sql commands")
        sql = fh.read()
    try:
        logger.info("setting up temp tables")
        DB_V2.execute(session, temp_table_multipliers)
        DB_V2.execute(session, temp_table_pricing)
        DB_V2.execute(session, insert_multipliers, m_records)
        DB_V2.execute(session, insert_pricing, p_records)
        date_param = dict(ed=str(effective_date))
        result = DB_V2.execute(session, sql, params=date_param)
        logger.info("Price update successful")
    except Exception as e:
        logger.info("An error occured while trying to update pricing")
        logger.error(e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return 200
    finally:
        drop_ = """
            DROP TABLE IF EXISTS atco_multipliers;
            DROP TABLE IF EXISTS atco_pricing;
        """
        DB_V2.execute(session, drop_)


def _adp_cp_series_handler(sheet: ADPProductSheet, df: DataFrame):
    match sheet:
        case ADPProductSheet.CP_A1:
            txv = (7, 9)
        case ADPProductSheet.CP_A2L:
            txv = ("A", "B", "C")
        case _:
            raise Exception(f"Improper sheet passed to the CP series handler {sheet}")

    txv_str = str(txv).replace("'", "").replace('"', "").replace(" ", "")
    product_rows, product_cols = ((3, None), (1, 4))
    product = df.iloc[slice(*product_rows), slice(*product_cols)]
    product.columns = ["cu", "al", "price"]
    product = product[~product["cu"].str.contains("Model Number")]

    cu = product[["cu", "price"]]
    al = product[["al", "price"]]
    txv_options = []
    for option in txv:
        cu_txv_option = cu[cu["cu"].str.contains(txv_str, regex=False)]
        cu_txv_option.loc[:, "cu"] = cu_txv_option["cu"].str.replace(
            txv_str, str(option), regex=False
        )
        txv_options.append(cu_txv_option.rename(columns={"cu": "key"}))

        al_txv_option = al[al["al"].str.contains(txv_str, regex=False)]
        al_txv_option.loc[:, "al"] = al_txv_option["al"].str.replace(
            txv_str, str(option), regex=False
        )
        txv_options.append(al_txv_option.rename(columns={"al": "key"}))

    cu = cu[~cu["cu"].str.contains(txv_str, regex=False)].rename(columns={"cu": "key"})
    al = al[~al["al"].str.contains(txv_str, regex=False)].rename(columns={"al": "key"})
    result = concat([cu, al, *txv_options], ignore_index=True)
    if sheet == ADPProductSheet.CP_A1:
        addition_right_hand = result.copy()
        addition_right_hand["key"] += "R"
        result = concat([result, addition_right_hand], ignore_index=True)
    result["vendor_id"] = VendorId.ADP.value
    result["series"] = "CP"
    result["price"] *= 100
    return result


def _adp_adder_expansion(
    adder_mapping: dict[str, list[str]], adder_df: DataFrame, series: ADPProductSheet
) -> DataFrame:
    adder_df["description"] = adder_df["description"].str.replace(" ", "").str.lower()
    adder_name_mapping = DataFrame(
        [
            (k.replace(" ", "").lower(), v)
            for k, v_list in adder_mapping.items()
            for v in v_list
        ],
        columns=["description", "key"],
    )
    adder_df_result = adder_df.merge(
        adder_name_mapping,
        on="description",
        how="left",
    ).explode("key")[["key", "price"]]
    adder_df_result["vendor_id"] = VendorId.ADP.value
    adder_df_result["series"] = series.name
    adder_df_result["price"] *= 100
    return adder_df_result.dropna().drop_duplicates()


async def _adp_update_zero_disc_prices(
    session: Session, effective_date: datetime
) -> None:
    logger.info("Background update process begun")
    all_models_sql = """
        SELECT vpbc.id, vp.vendor_product_identifier
        FROM vendor_pricing_by_class vpbc
        JOIN vendor_products vp
            ON vp.id = vpbc.product_id
            AND vp.vendor_id = 'adp'
        JOIN vendor_pricing_classes price_classes
            ON price_classes.id = vpbc.pricing_class_id
            AND price_classes.vendor_id = 'adp'
        WHERE price_classes.name = 'ZERO_DISCOUNT';
    """
    try:
        logger.info("Retrieving all Zero Discount products with price ids")
        all_models = DB_V2.execute(session, all_models_sql).fetchall()
        logger.info(f"Repricing {len(all_models)} models ...")
        new_pricing_by_id = []
        for i, rec in enumerate(all_models):
            id_, model = rec
            logger.info(f"    {model} ({i+1} of {len(all_models)})")
            try:
                fresh_build = parse_model_string(
                    session, 0, model, ParsingModes.BASE_PRICE
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
        update_setup = """
            DROP TABLE IF EXISTS adp_zd;
            CREATE TEMPORARY TABLE adp_zd (id int, price int);
        """
        populate_update = """
            INSERT INTO adp_zd (id, price)
            VALUES (:id, :price)
        """
        update_pricing = """
            UPDATE vendor_pricing_by_class
            SET price = new.price, effective_date = :ed
            FROM adp_zd AS new
            WHERE new.id = vendor_pricing_by_class.id;
        """
        try:
            DB_V2.execute(session, update_setup)
            DB_V2.execute(session, populate_update, new_pricing_params)
            logger.info("temp table setup")
            DB_V2.execute(session, update_pricing, dict(ed=effective_date))
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
    all_models_sql = """
        SELECT vpbc.id, vp.vendor_product_identifier, vpbc.vendor_customer_id, 
            a.value private_label
        FROM vendor_pricing_by_customer vpbc
        JOIN vendor_products vp
            ON vp.id = vpbc.product_id
            AND vp.vendor_id = 'adp'
        LEFT JOIN vendor_pricing_by_customer_attrs a
            ON a.pricing_by_customer_id = vpbc.id
            AND a.attr = 'private_label'
    """
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
                    session, customer_id, model, ParsingModes.CUSTOMER_PRICING
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
        update_setup = """
            DROP TABLE IF EXISTS adp_customer_nets;
            CREATE TEMPORARY TABLE adp_customer_nets (id int, price int);
        """
        populate_update = """
            INSERT INTO adp_customer_nets (id, price)
            VALUES (:id, :price)
        """
        update_pricing = """
            UPDATE vendor_pricing_by_customer
            SET price = new.price, effective_date = :ed
            FROM adp_customer_nets AS new
            WHERE new.id = vendor_pricing_by_customer.id;
        """
        try:
            DB_V2.execute(session, update_setup)
            DB_V2.execute(session, populate_update, new_pricing_params)
            logger.info("temp table setup")
            DB_V2.execute(session, update_pricing, dict(ed=effective_date))
            DB_V2.execute(session, "DROP TABLE IF EXISTS adp_customer_nets;")
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
        results = []
        for series, df in product_pricing_sheets.items():
            logger.info(f"processing sheet: {series}")
            match series:
                case ADPProductSheet.B:
                    __composed_attrs = {
                        (
                            "130 deg F Aquastat (for HW coil only)",
                            "120V [1]",
                        ): "adder_voltage_4"
                    }
                    __adder_name_mapping = {
                        "HP-AC TXV (All)": [
                            "adder_metering_A",
                            "adder_metering_B",
                            "adder_metering_9",
                        ],
                        "Variable Speed Motor": ["adder_motor_V"],
                        "120V [1]": ["adder_voltage_3"],
                        "HW Pump Assy": ["adder_heat_P"],
                        "Refrigerant Detection System": ["adder_RDS_R"],
                    }
                    product_1_rows, product_1_cols = ((9, 57), (1, 8))
                    product_2_rows, product_2_cols = ((9, 49), (10, 17))
                    adder_rows, adder_cols = ((52, 58), (9, 17))

                    product_1 = df.iloc[slice(*product_1_rows), slice(*product_1_cols)]
                    product_2 = df.iloc[slice(*product_2_rows), slice(*product_2_cols)]
                    adders = df.iloc[slice(*adder_rows), slice(*adder_cols)]

                    product_1.dropna(axis=1, how="all", inplace=True)
                    product_2.dropna(axis=1, how="all", inplace=True)
                    adders.dropna(axis=1, how="all", inplace=True)

                    product_cols = ["tonnage", "slab", "base", "2", "3", "4"]
                    product_1.columns = product_cols
                    product_2.columns = product_cols
                    adders.columns = ["description", "price"]

                    product_1.loc[:, "slab"] = (
                        product_1["slab"].str.strip().str.slice(0, 2)
                    )
                    product_2.loc[:, "slab"] = (
                        product_2["slab"].str.strip().str.slice(0, 2)
                    )

                    product_1.dropna(how="all", inplace=True)
                    product_2.dropna(how="all", inplace=True)

                    product_1.loc[:, "tonnage"].ffill(inplace=True)
                    product_2.loc[:, "tonnage"].ffill(inplace=True)

                    for composed, name in __composed_attrs.items():
                        new_adder = Series(
                            adders[adders["description"].isin(composed)]["price"].sum(),
                            index=[name],
                            name="price",
                        ).reset_index()
                        new_adder["description"] = new_adder.pop("index")
                        adders = concat([adders, new_adder])
                    adder_name_mapping = DataFrame(
                        [
                            (k, v)
                            for k, v_list in __adder_name_mapping.items()
                            for v in v_list
                        ],
                        columns=["description", "key"],
                    )
                    adders_result = adders.merge(
                        adder_name_mapping,
                        on="description",
                        how="left",
                    ).explode("key")
                    adders_result["key"] = adders_result["key"].fillna(
                        adders_result["description"]
                    )
                    adders_result = adders_result[
                        ~adders_result["description"].str.contains("Aquastat")
                    ][["key", "price"]]

                    result = concat(
                        [
                            product_1.melt(
                                id_vars=["tonnage", "slab"],
                                var_name="suffix",
                                value_name="price",
                            ),
                            product_2.melt(
                                id_vars=["tonnage", "slab"],
                                var_name="suffix",
                                value_name="price",
                            ),
                        ]
                    )
                    result.loc[:, "key"] = (
                        result["tonnage"].astype(str)
                        + "_"
                        + result["slab"]
                        + "_"
                        + result["suffix"]
                    )
                    result = concat([result[["key", "price"]], adders_result])
                    result["vendor_id"] = VendorId.ADP.value
                    result["series"] = series.name
                    result["price"] *= 100
                    results.append(result)
                case ADPProductSheet.CP_A1 | ADPProductSheet.CP_A2L:
                    results.append(_adp_cp_series_handler(series, df))
                case ADPProductSheet.F:
                    __adder_name_mapping = {
                        "HP-AC TXV (All)": [
                            "adder_metering_A",
                            "adder_metering_B",
                            "adder_metering_9",
                        ],
                        "HP Expansion Valve R-410A (bleed or non-bleed)": [
                            "adder_metering_A",
                            "adder_metering_B",
                            "adder_metering_9",
                        ],
                        "Circuit Breaker (adder for 5kW only)": ["adder_line_conn_B"],
                        "120V PSC or 120V ECM": ["adder_voltage_3", "adder_voltage_4"],
                        "5-speedECM18-37": [
                            "adder_tonnage_18",
                            "adder_tonnage_24",
                            "adder_tonnage_25",
                            "adder_tonnage_30",
                            "adder_tonnage_31",
                            "adder_tonnage_36",
                            "adder_tonnage_37",
                        ],
                        "5-speedECM42-48": [
                            "adder_tonnage_42",
                            "adder_tonnage_48",
                        ],
                        "5-speedECM60": [
                            "adder_tonnage_60",
                        ],
                        "Refrigerant Detection System": ["adder_RDS_R"],
                    }
                    product_1_rows, product_1_cols = ((8, 47), (1, 10))
                    product_2_rows, product_2_cols = ((8, 29), (15, 25))
                    adder_rows, adder_cols = ((30, 38), (16, 23))

                    product_1 = df.iloc[slice(*product_1_rows), slice(*product_1_cols)]
                    product_2 = df.iloc[slice(*product_2_rows), slice(*product_2_cols)]

                    adders = df.iloc[slice(*adder_rows), slice(*adder_cols)]
                    adders.dropna(how="all", axis=1, inplace=True)
                    adders.iloc[:, 0].ffill(inplace=True)
                    mask = ~adders.iloc[:, 1].isna()
                    adders.iloc[mask, 0] = adders.loc[mask].iloc[:, 0].str.replace(
                        " ", ""
                    ) + adders.loc[mask].iloc[:, 1].astype(str).str.replace(" ", "")
                    adders.iloc[:, 0] = (
                        adders.iloc[:, 0].str.replace(" ", "").str.lower()
                    )
                    adders = adders.iloc[:, [0, 2]]
                    adders.columns = ["description", "price"]
                    results.append(
                        _adp_adder_expansion(__adder_name_mapping, adders, series)
                    )

                    for pt in (product_1, product_2):
                        pt.dropna(axis=1, how="all", inplace=True)
                        pt.dropna(axis=0, how="all", inplace=True)
                        pt.iloc[:, 0] = pt.iloc[:, 0].ffill()
                        pt.iloc[:, 1] = (
                            pt.iloc[:, 1]
                            .str.replace(",", "|", regex=False)
                            .str.replace(" ", "", regex=False)
                        )
                        col_names = [
                            "tonnage",
                            "slab",
                            "base",
                            "05",
                            "07",
                            "10",
                            "15",
                            "20",
                        ]
                        if pt.shape[1] == 8:
                            pt.columns = col_names
                        elif pt.shape[1] == 7:
                            pt.columns = col_names[:-1]
                        else:
                            raise Exception(f"Unexpected Column Count: {pt.shape}")
                        pt = pt.melt(
                            id_vars=["tonnage", "slab"],
                            var_name="suffix",
                            value_name="price",
                        )
                        pt.loc[:, "key"] = (
                            pt.pop("tonnage").astype(str)
                            + "_"
                            + pt.pop("slab")
                            + "_"
                            + pt.pop("suffix")
                        )
                        result = pt[["key", "price"]]
                        result["vendor_id"] = VendorId.ADP.value
                        result["series"] = series.name
                        result["price"] *= 100
                        results.append(result)
                case ADPProductSheet.S:
                    __adder_name_mapping = {
                        "HP Expansion Valve": [
                            "adder_metering_A",
                            "adder_metering_B",
                            "adder_metering_9",
                        ],
                        "5-speed ECM": [
                            "adder_tonnage_19",
                            "adder_tonnage_25",
                            "adder_tonnage_31",
                            "adder_tonnage_37",
                        ],
                        "Refrigerant Detection System": ["adder_RDS_R"],
                    }
                    product_rows, product_cols = ((11, 26), (1, 5))
                    adder_rows, adder_cols = ((29, 32), (5, 9))

                    product = df.iloc[slice(*product_rows), slice(*product_cols)]
                    product = product.dropna(how="all", axis=0).dropna(
                        how="all", axis=1
                    )
                    product.columns = ["slab", "00", "05", "07"]
                    product.loc[:, "10"] = product["07"]
                    product.loc[:, "slab"] = product["slab"].str.strip().str.slice(1, 3)
                    result = product.melt(
                        id_vars="slab", var_name="heat", value_name="price"
                    )
                    result.loc[:, "key"] = result["slab"] + "_" + result["heat"]
                    result = result[["key", "price"]]
                    result["vendor_id"] = VendorId.ADP.value
                    result["series"] = series.name
                    result["price"] *= 100
                    results.append(result)

                    adders = df.iloc[slice(*adder_rows), slice(*adder_cols)]
                    adders.dropna(how="all", axis=1, inplace=True)
                    adders.columns = ["description", "price"]
                    adders["description"] = (
                        adders["description"].str.replace(" ", "").str.lower()
                    )
                    adder_name_mapping = DataFrame(
                        [
                            (k.replace(" ", "").lower(), v)
                            for k, v_list in __adder_name_mapping.items()
                            for v in v_list
                        ],
                        columns=["description", "key"],
                    )
                    adders_result = adders.merge(
                        adder_name_mapping,
                        on="description",
                        how="left",
                    ).explode("key")[["key", "price"]]
                    adders_result["vendor_id"] = VendorId.ADP.value
                    adders_result["series"] = series.name
                    adders_result["price"] *= 100
                    results.append(adders_result)
                case ADPProductSheet.AMH:
                    product_rows, product_cols = ((10, 34), (2, 5))
                    product = df.iloc[slice(*product_rows), slice(*product_cols)]
                    product = (
                        product.dropna(how="all", axis=0)
                        .dropna(how="all", axis=1)
                        .iloc[:, [0, 2]]
                    )
                    product.columns = ["key", "price"]
                    product["vendor_id"] = VendorId.ADP.value
                    product["series"] = series.name
                    product["price"] *= 100
                    results.append(product)
                case ADPProductSheet.HE:
                    __adder_name_mapping = {
                        "HP / AC TXV (All)": [
                            "adder_metering_A",
                            "adder_metering_B",
                            "adder_metering_9",
                            "adder_metering_7",
                        ],
                        'Factory Installed ("R")': ["adder_RDS_R"],
                        'Field Installed ("N")': ["adder_RDS_N"],
                        'Factory Installed ("L")': ["adder_RDS_L"],
                        "Non-core Depth": ["adder_misc_non-core"],
                        "Non-core Hand": ["adder_misc_non-core"],
                    }
                    product_1_rows, product_1_cols = ((11, 28), (1, 7))
                    product_2_rows, product_2_cols = ((11, 40), (10, 16))
                    adders_rows, adders_cols = ((42, 55), (9, 13))

                    product_1 = df.iloc[slice(*product_1_rows), slice(*product_1_cols)]
                    product_2 = df.iloc[slice(*product_2_rows), slice(*product_2_cols)]
                    adders = df.iloc[slice(*adders_rows), slice(*adders_cols)]
                    adders.dropna(how="all", axis=1, inplace=True)
                    adders.columns = ["description", "price"]
                    adders.dropna(subset="price", inplace=True)
                    results.append(
                        _adp_adder_expansion(__adder_name_mapping, adders, series)
                    )

                    for product_df in (product_1, product_2):
                        product_df.columns = [
                            "slab",
                            "uncased",
                            "embossed_cased",
                            "painted_cased",
                            "embossed_mp",
                            "painted_mp",
                        ]
                        product_df.loc[:, "slab"] = (
                            product_df["slab"]
                            .str.replace("*", "")
                            .str.strip()
                            .str.slice(-2, None)
                        )
                        result = product_df.melt(
                            id_vars="slab", var_name="suffix", value_name="price"
                        )
                        result = result[result["price"] > 0]
                        result.loc[:, "key"] = result["slab"] + "_" + result["suffix"]

                        result = result[["key", "price"]]
                        result["vendor_id"] = VendorId.ADP.value
                        result["series"] = series.name
                        result["price"] *= 100
                        results.append(result)
                case ADPProductSheet.HH:
                    __adder_name_mapping = {
                        "HP / AC TXV (All)": [
                            "adder_metering_A",
                            "adder_metering_B",
                            "adder_metering_9",
                            "adder_metering_7",
                        ],
                        'Factory Installed ("R")': ["adder_RDS_R"],
                        'Field Installed ("N")': ["adder_RDS_N"],
                        'Factory Installed ("L")': ["adder_RDS_L"],
                    }
                    product_rows, product_cols = ((15, 22), (0, 4))
                    adders_rows, adders_cols = ((24, 33), (0, 4))

                    product = df.iloc[slice(*product_rows), slice(*product_cols)]
                    product = product.dropna(how="all", axis=1).dropna(
                        how="all", axis=0
                    )
                    product = product.iloc[:, [0, -1]]
                    product.columns = ["key", "price"]
                    product.loc[:, "key"] = (
                        product["key"].str.strip().str.slice(-2, None)
                    )
                    product["vendor_id"] = VendorId.ADP.value
                    product["series"] = series.name
                    product["price"] *= 100
                    results.append(product)

                    adders = df.iloc[slice(*adders_rows), slice(*adders_cols)]
                    adders.dropna(how="all", axis=1, inplace=True)
                    adders.columns = ["description", "price"]
                    adders.dropna(subset="price", inplace=True)
                    results.append(
                        _adp_adder_expansion(__adder_name_mapping, adders, series)
                    )
                case ADPProductSheet.MH:
                    __adder_name_mapping = {
                        "HP / AC TXV (All)": [
                            "adder_metering_A",
                            "adder_metering_B",
                            "adder_metering_9",
                            "adder_metering_7",
                        ],
                        'Factory Installed ("R")': ["adder_RDS_R"],
                        'Field Installed ("N")': ["adder_RDS_N"],
                        'Factory Installed ("L")': ["adder_RDS_L"],
                    }
                    product_rows, product_cols = ((13, 30), (0, 4))
                    adders_rows, adders_cols = ((33, 42), (0, 4))

                    product = df.iloc[slice(*product_rows), slice(*product_cols)]
                    product = product.dropna(how="all", axis=1).dropna(
                        how="all", axis=0
                    )
                    product = product.iloc[:, [0, -1]]
                    product.columns = ["key", "price"]
                    product.loc[:, "key"] = (
                        product["key"].str.strip().str.slice(-2, None)
                    )
                    product["vendor_id"] = VendorId.ADP.value
                    product["series"] = series.name
                    product["price"] *= 100
                    results.append(product)

                    adders = df.iloc[slice(*adders_rows), slice(*adders_cols)]
                    adders.dropna(how="all", axis=1, inplace=True)
                    adders.columns = ["description", "price"]
                    adders.dropna(subset="price", inplace=True)
                    results.append(
                        _adp_adder_expansion(__adder_name_mapping, adders, series)
                    )
                case ADPProductSheet.V:
                    __adder_name_mapping = {
                        "HP / AC TXV (All)": [
                            "adder_metering_A",
                            "adder_metering_B",
                            "adder_metering_9",
                            "adder_metering_7",
                        ],
                        'Factory Installed ("R")': ["adder_RDS_R"],
                        'Field Installed ("N")': ["adder_RDS_N"],
                        'Factory Installed ("L")': ["adder_RDS_L"],
                    }
                    product_1_rows, product_1_cols = ((11, 29), (0, 5))
                    product_2_rows, product_2_cols = ((11, 30), (6, 11))
                    adders_rows, adders_cols = ((33, 42), (0, 4))

                    product_1 = df.iloc[slice(*product_1_rows), slice(*product_1_cols)]
                    product_2 = df.iloc[slice(*product_2_rows), slice(*product_2_cols)]
                    adders = df.iloc[slice(*adders_rows), slice(*adders_cols)]
                    adders.dropna(how="all", axis=1, inplace=True)
                    adders.columns = ["description", "price"]
                    adders.dropna(subset="price", inplace=True)
                    results.append(
                        _adp_adder_expansion(__adder_name_mapping, adders, series)
                    )

                    for product_df in (product_1, product_2):
                        product_df.columns = [
                            "slab",
                            "tonnage",
                            "height",
                            "embossed",
                            "painted",
                        ]
                        product_df.loc[:, "slab"] = (
                            product_df["slab"]
                            .str.replace("*", "")
                            .str.strip()
                            .str.slice(-2, None)
                            .astype(int)
                        )
                        result = product_df.melt(
                            id_vars=["slab", "tonnage", "height"],
                            var_name="suffix",
                            value_name="price",
                        )
                        result = result[result["price"] > 0]
                        result.loc[:, "key"] = (
                            result["slab"].astype(str) + "_" + result["suffix"]
                        )

                        result = result[["key", "price"]]
                        result["vendor_id"] = VendorId.ADP.value
                        result["series"] = series.name
                        result["price"] *= 100
                        results.append(result)
                case ADPProductSheet.HD:
                    __adder_name_mapping = {
                        "HP / AC TXV (All)": [
                            "adder_metering_A",
                            "adder_metering_B",
                            "adder_metering_9",
                            "adder_metering_7",
                        ],
                        'Factory Installed ("R")': ["adder_RDS_R"],
                        'Field Installed ("N")': ["adder_RDS_N"],
                        'Factory Installed ("L")': ["adder_RDS_L"],
                    }
                    product_1_rows, product_1_cols = ((11, 28), (1, 5))
                    product_2_rows, product_2_cols = ((11, 27), (6, 10))
                    adders_rows, adders_cols = ((33, 42), (0, 4))

                    product_1 = df.iloc[slice(*product_1_rows), slice(*product_1_cols)]
                    product_2 = df.iloc[slice(*product_2_rows), slice(*product_2_cols)]
                    adders = df.iloc[slice(*adders_rows), slice(*adders_cols)]
                    adders.dropna(how="all", axis=1, inplace=True)
                    adders.columns = ["description", "price"]
                    adders.dropna(subset="price", inplace=True)
                    results.append(
                        _adp_adder_expansion(__adder_name_mapping, adders, series)
                    )

                    for product_df in (product_1, product_2):
                        product_df.columns = [
                            "slab",
                            "tonnage",
                            "embossed",
                            "painted",
                        ]
                        product_df.loc[:, "slab"] = (
                            product_df["slab"]
                            .str.replace("*", "")
                            .str.strip()
                            .str.slice(-2, None)
                            .astype(int)
                            .astype(str)
                        )
                        result = product_df.melt(
                            id_vars=["slab", "tonnage"],
                            var_name="suffix",
                            value_name="price",
                        )
                        result = result[result["price"] > 0]
                        result.loc[:, "key"] = result[["slab", "suffix"]].apply(
                            "_".join, 1
                        )

                        result = result[["key", "price"]]
                        result["vendor_id"] = VendorId.ADP.value
                        result["series"] = series.name
                        result["price"] *= 100
                        results.append(result)
                case ADPProductSheet.SC:
                    product_rows, product_cols = ((16, 41), (2, 5))

                    product = df.iloc[slice(*product_rows), slice(*product_cols)]
                    product = product.dropna(how="all", axis=1).dropna(
                        how="all", axis=0
                    )
                    product.columns = ["key", "0", "1"]
                    product.dropna(subset="key", inplace=True)
                    product = product[
                        ~(product["key"].str.strip().str.startswith("Service"))
                        & ~(product["key"].str.strip().str.startswith("Model"))
                    ]
                    product.loc[:, "key"] = (
                        product["key"]
                        .str.replace("(", "[", regex=False)
                        .str.replace(")", "]", regex=False)
                        .str.replace(" ", "", regex=False)
                    )
                    result = product.melt(
                        id_vars="key", var_name="suffix", value_name="price"
                    )
                    result.dropna(inplace=True)
                    result.loc[:, "key"] += "_" + result["suffix"]
                    result = result[["key", "price"]]
                    result["vendor_id"] = VendorId.ADP.value
                    result["series"] = series.name
                    result["price"] *= 100
                    results.append(result)
                case ADPProductSheet.PARTS:
                    df = df.iloc[4:, :5]
                    df.columns = [
                        "part_number",
                        "description",
                        "pkg_qty",
                        "preferred",
                        "standard",
                    ]
                    df.loc[:, "preferred"] = (
                        to_numeric(df["preferred"], errors="coerce") * 100
                    )
                    df.loc[:, "standard"] = (
                        to_numeric(df["standard"], errors="coerce") * 100
                    )
                    df.dropna(subset="part_number", inplace=True)
                    df.replace({nan: None}, inplace=True)
                    df_records = df.to_dict(orient="records")

                    sql_resources = SQL[series]
                    setup_ = sql_resources[DBOps.SETUP]
                    populate_parts_temp = sql_resources[DBOps.POPULATE_TEMP]
                    update_parts = sql_resources[DBOps.UPDATE_EXISTING]
                    insert_new_parts = sql_resources[DBOps.INSERT_NEW_PRODUCT]
                    # expecting returned ids from prior insert for next queries
                    define_pkg_qtys_for_new_parts = sql_resources[DBOps.SETUP_ATTRS]
                    insert_new_prices = sql_resources[DBOps.INSERT_NEW_PRODUCT_PRICING]
                    update_customer_prices = sql_resources[
                        DBOps.UPDATE_CUSTOMER_PRICING
                    ]
                    eff_date_param = dict(ed=effective_date)

                    session.begin()
                    try:
                        DB_V2.execute(session, setup_)
                        DB_V2.execute(session, populate_parts_temp, df_records)
                        DB_V2.execute(session, update_parts, eff_date_param)
                        new_ids = tuple(
                            [
                                rec[0]
                                for rec in DB_V2.execute(
                                    session, insert_new_parts
                                ).fetchall()
                            ]
                        )
                        if new_ids:
                            new_ids_param = dict(new_part_ids=new_ids)
                            DB_V2.execute(
                                session, define_pkg_qtys_for_new_parts, new_ids_param
                            )
                            DB_V2.execute(
                                session,
                                insert_new_prices,
                                new_ids_param | eff_date_param,
                            )
                        DB_V2.execute(session, update_customer_prices, eff_date_param)
                    except Exception as e:
                        import traceback as tb

                        logger.error(tb.format_exc())
                        session.rollback()
                    else:
                        session.commit()
                    finally:
                        session.close()

        all_keys = concat(results, ignore_index=True)
        all_keys.loc[:, "effective_date"] = effective_date
        setup_ = """
            DROP TABLE IF EXISTS adp_product_series_pricing_update;
            CREATE TEMPORARY TABLE adp_product_series_pricing_update (
                vendor_id varchar,
                series varchar,
                key varchar,
                price int,
                effective_date timestamp
            );
        """
        additional_setup = """
            INSERT INTO adp_product_series_pricing_update
            VALUES (:vendor_id, :series, :key, :price, :effective_date);
        """
        key_update_sql = """
            UPDATE vendor_product_series_pricing
            SET price = new.price, effective_date = new.effective_date
            FROM adp_product_series_pricing_update AS new
            WHERE new.vendor_id = vendor_product_series_pricing.vendor_id
            AND new.series = vendor_product_series_pricing.series
            AND new.key = vendor_product_series_pricing.key
            RETURNING *;
        """
        teardown = """
            DROP TABLE IF EXISTS adp_product_series_pricing_update;
        """
        records = all_keys.dropna().to_dict(orient="records")
        logger.info("updating records")
        session.begin()
        DB_V2.execute(session, setup_)
        DB_V2.execute(session, additional_setup, params=records)
        update_result = DB_V2.execute(session, key_update_sql).mappings().fetchall()
        logger.info("tearing down")
        DB_V2.execute(session, teardown)
        bg.add_task(
            _adp_update_zero_disc_prices,
            session=session,
            effective_date=effective_date,
        )
        return 202
    else:
        for sheet, df in customer_reference_sheets.items():
            setup_new_customers = """
                CREATE TEMPORARY TABLE adp_customers (customer varchar);
            """
            populate_new_customers = """
                INSERT INTO adp_customers VALUES (:customer);
            """
            add_new_customers = """
                INSERT INTO vendor_customers (vendor_id, name)
                SELECT 'adp' vendor_id, customer
                FROM adp_customers
                WHERE adp_customers.customer NOT IN (
                    SELECT DISTINCT name
                    FROM vendor_customers a
                    WHERE vendor_id = 'adp'
                );
            """
            teardown = """
                DROP TABLE IF EXISTS adp_customers;
                DROP TABLE IF EXISTS adp_mgds;
            """
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
                    setup_mg_update = """
                        CREATE TEMPORARY TABLE adp_mgds (
                            customer varchar,
                            mg char(2),
                            discount float);
                    """
                    populate_mg_update = """
                        INSERT INTO adp_mgds
                        VALUES (:customer, :mg, :discount);
                    """
                    update_discounts = """
                        UPDATE vendor_product_class_discounts
                        SET discount = new.discount, effective_date = :ed
                        FROM adp_mgds as new
                        JOIN vendor_product_classes vp_class
                            ON vp_class.name = new.mg
                            AND vp_class.rank = 2
                            AND vp_class.vendor_id = 'adp'
                        JOIN vendor_customers vc
                            ON vc.name = new.customer
                            AND vc.vendor_id = 'adp'
                        WHERE vp_class.id = product_class_id
                            AND vc.id = vendor_customer_id
                        RETURNING *;
                    """
                    add_new_customer_discounts = """
                        INSERT INTO vendor_product_class_discounts (
                            product_class_id, vendor_customer_id, 
                            discount, effective_date)
                        SELECT vp_class.id, vc.id, new.discount, :ed
                        FROM adp_mgds as new
                        JOIN vendor_product_classes vp_class
                            ON vp_class.name = new.mg
                            AND vp_class.rank = 2
                            AND vp_class.vendor_id = 'adp'
                        JOIN vendor_customers vc
                            ON vc.name = new.customer
                            AND vc.vendor_id = 'adp'
                        WHERE NOT EXISTS (
                            SELECT 1 
                            FROM vendor_product_class_discounts a
                            WHERE a.vendor_customer_id = vc.id
                                AND a.product_class_id = vp_class.id
                            )
                        RETURNING *;
                    """
                    delete_missing_discounts = """
                        UPDATE vendor_product_class_discounts
                        SET deleted_at = CURRENT_TIMESTAMP
                        WHERE NOT EXISTS (
                            SELECT 1 
                            FROM vendor_product_class_discounts a
                            JOIN vendor_product_classes vp_class
                                ON vp_class.rank = 2
                                AND vp_class.vendor_id = 'adp'
                                AND vp_class.id = a.product_class_id
                            JOIN vendor_customers vc
                                ON vc.vendor_id = 'adp'
                                AND a.vendor_customer_id = vc.id
                            JOIN adp_mgds as new
                                ON vp_class.name = new.mg
                                AND vc.name = new.customer
                            WHERE a.id = vendor_product_class_discounts.id
                            );
                    """

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
                        DB_V2.execute(session, delete_missing_discounts)
                        DB_V2.execute(session, teardown)
                    except Exception as e:
                        import traceback as tb

                        print(tb.format_exc())
                        session.rollback()
                    else:
                        logger.info(f"update succesful")
                        session.commit()

                case ADPCustomerRefSheet.SPECIAL_NET:
                    df = df[
                        ["Customer Name", "Material", "Material Description", "Price"]
                    ]
                    df.columns = ["customer", "part_id", "description", "price"]
                    df.loc[:, "description"] = (
                        df["description"]
                        .str.split("  ", n=1, expand=True)[0]
                        .str.strip()
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

                    setup_snp_update = """
                        DROP TABLE IF EXISTS adp_snps;
                        CREATE TEMPORARY TABLE adp_snps (
                            customer varchar,
                            description varchar,
                            price int
                        );
                    """
                    populate_snp_update = """
                        INSERT INTO adp_snps
                        VALUES (:customer, :description, :price);
                    """
                    update_snps = """
                        UPDATE vendor_product_discounts
                        SET discount = (1-(new.price::float / class_price.price::float))*100,
                            effective_date = :ed
                        FROM adp_snps AS new
                        JOIN vendor_customers vc
                            ON vc.name = new.customer
                            AND vc.vendor_id = 'adp'
                        JOIN vendor_products vp
                            ON vp.vendor_product_identifier = new.description
                            AND vp.vendor_id = 'adp'
                        JOIN vendor_pricing_by_class AS class_price
                            ON class_price.product_id = vp.id
                        WHERE EXISTS (
                            SELECT 1
                            FROM vendor_pricing_classes pricing_classes
                            WHERE pricing_classes.id = class_price.pricing_class_id
                            AND pricing_classes.name = 'ZERO_DISCOUNT'
                            AND pricing_classes.vendor_id = 'adp'
                        )
                        AND vendor_product_discounts.product_id = vp.id
                        AND vendor_product_discounts.vendor_customer_id = vc.id;
                    """
                    # TODO figure out how to incorporate private labels
                    add_new_snps = """
                        INSERT INTO vendor_product_discounts (
                            product_id, 
                            vendor_customer_id,
                            discount,
                            effective_date
                        )
                        SELECT vp.id, vc.id,
                            (1-(new.price::float / class_price.price::float))*100, :ed
                        FROM adp_snps AS new
                        JOIN vendor_customers vc
                            ON vc.name = new.customer
                            AND vc.vendor_id = 'adp'
                        JOIN vendor_products vp
                            ON vp.vendor_product_identifier = new.description
                            AND vp.vendor_id = 'adp'
                        JOIN vendor_pricing_by_class AS class_price
                            ON class_price.product_id = vp.id
                        WHERE NOT EXISTS (
                            select 1
                            from vendor_product_discounts z
                            where z.product_id = vp.id
                            and z.vendor_customer_id = vc.id
                        );
                    """
                    delete_missing_snps = """
                    UPDATE vendor_product_discounts
                    SET deleted_at = CURRENT_TIMESTAMP
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM vendor_product_discounts vp_discounts
                        JOIN vendor_customers vc
                            ON vc.vendor_id = 'adp'
                            AND vc.id = vp_discounts.vendor_customer_id
                        JOIN vendor_products vp
                            ON vp.vendor_id = 'adp'
                            AND vp.id = vp_discounts.product_id
                        JOIN adp_snps AS new
                            ON vp.vendor_product_identifier = new.description
                            AND vc.name = new.customer
                        WHERE vp_discounts.id = vendor_product_discounts.id
                    );
                    """
                    logger.info("updating SNPs")
                    session.begin()
                    try:
                        DB_V2.execute(session, setup_snp_update)
                        DB_V2.execute(session, populate_snp_update, params=df_records)
                        DB_V2.execute(session, update_snps, params=eff_date_param)
                        DB_V2.execute(session, add_new_snps, params=eff_date_param)
                        DB_V2.execute(session, delete_missing_snps)
                        DB_V2.execute(
                            session,
                            "DROP TABLE IF EXISTS adp_snps;",
                        )
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
