from logging import getLogger
from pandas import DataFrame
from app.admin.models import VendorId, ADPProductSheet
from app.admin.price_sheet_parsers.adp import _adder_expansion

logger = getLogger("uvicorn.info")


def adp_coils_mh_sheet_parser(
    df: DataFrame, series: ADPProductSheet
) -> tuple[DataFrame, DataFrame]:
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
    product = product.dropna(how="all", axis=1).dropna(how="all", axis=0)
    product = product.iloc[:, [0, -1]]
    product.columns = ["key", "price"]
    product.loc[:, "key"] = product["key"].str.strip().str.slice(-2, None)
    product["vendor_id"] = VendorId.ADP.value
    product["series"] = series.name
    product["price"] *= 100

    adders = df.iloc[slice(*adders_rows), slice(*adders_cols)]
    adders.dropna(how="all", axis=1, inplace=True)
    adders.columns = ["description", "price"]
    adders.dropna(subset="price", inplace=True)
    result_adders = _adder_expansion.expand(__adder_name_mapping, adders, series)
    return product, result_adders
