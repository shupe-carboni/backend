from datetime import datetime
from typing import Annotated
from fastapi import HTTPException, Depends, UploadFile, status, Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app import auth
from app.db import DB_V2
from numpy import nan
from pandas import read_csv, ExcelFile, DataFrame, concat, Series
import logging
import os
from app.admin.models import VendorId

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
            adp_price_update(session, file_df_collection, effective_date)
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


def adp_price_update(
    session: Session, dfs: dict[str, DataFrame], effective_date: datetime
):
    """
    ADP keeps separate files for air handlers and coils. This method will handle either
    one, but ultimately two requests will be needed to complete a full update on
    products PLUS an additional request just for parts/accessories.

    Each file will have stylized pricing that needs to be formatted for updates to
    *vendor_product_series_pricing*. This table schema has product Series
    """
    from app.admin.models import ADPProductSheet, ADPSeries

    product_pricing_sheets = {
        ADPSeries[ADPProductSheet(sn).name]: df
        for sn, df in dfs.items()
        if sn in ADPProductSheet.__members__.values()
    }
    results = []
    for series, df in product_pricing_sheets.items():
        match series:
            case ADPSeries.B:
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

                product_1.loc[:, "slab"] = product_1["slab"].str.strip().str.slice(0, 2)
                product_2.loc[:, "slab"] = product_2["slab"].str.strip().str.slice(0, 2)

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
                result["series"] = series.value
                result["price"] *= 100

            case ADPSeries.CP_A1:
                ...
            case ADPSeries.CP_A2L:
                ...
            case ADPSeries.F:
                ...
            case ADPSeries.S:
                ...
            case ADPSeries.M_FURNACE:
                ...
    return
