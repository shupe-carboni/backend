from logging import getLogger
from pandas import DataFrame
from app.admin.models import VendorId, ADPProductSheet
from app.admin.price_updates.price_sheet_parsers.adp import _adder_expansion

logger = getLogger("uvicorn.info")


def adp_coils_he_sheet_parser(
    df: DataFrame, series: ADPProductSheet
) -> list[DataFrame]:
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
    adders_result = _adder_expansion.expand(__adder_name_mapping, adders, series)
    results = []
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
            product_df["slab"].str.replace("*", "").str.strip().str.slice(-2, None)
        )
        result = product_df.melt(id_vars="slab", var_name="suffix", value_name="price")
        result = result[result["price"] > 0]
        result.loc[:, "key"] = result["slab"] + "_" + result["suffix"]

        result = result[["key", "price"]]
        result["vendor_id"] = VendorId.ADP.value
        result["series"] = series.name
        result["price"] *= 100
        results.append(result)
    return [*results, adders_result]
