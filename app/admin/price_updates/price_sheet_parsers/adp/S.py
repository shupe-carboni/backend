from logging import getLogger
from pandas import DataFrame
from app.admin.models import VendorId, ADPProductSheet
from app.admin.price_updates.price_sheet_parsers.adp import _adder_expansion

logger = getLogger("uvicorn.info")


def adp_ahs_s_sheet_parser(
    df: DataFrame, series: ADPProductSheet
) -> tuple[DataFrame, DataFrame]:
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
    product = product.dropna(how="all", axis=0).dropna(how="all", axis=1)
    product.columns = ["slab", "00", "05", "07"]
    product.loc[:, "10"] = product["07"]
    product.loc[:, "slab"] = product["slab"].str.strip().str.slice(1, 3)
    result = product.melt(id_vars="slab", var_name="heat", value_name="price")
    result.loc[:, "key"] = result["slab"] + "_" + result["heat"]
    result = result[["key", "price"]]
    result["vendor_id"] = VendorId.ADP.value
    result["series"] = series.name
    result["price"] *= 100

    adders = df.iloc[slice(*adder_rows), slice(*adder_cols)]
    adders.dropna(how="all", axis=1, inplace=True)
    adders.columns = ["description", "price"]
    adders_result = _adder_expansion.expand(__adder_name_mapping, adders, series)
    return result, adders_result
