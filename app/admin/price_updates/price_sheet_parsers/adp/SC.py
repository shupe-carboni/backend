from logging import getLogger
from pandas import DataFrame
from app.admin.models import VendorId, ADPProductSheet

logger = getLogger("uvicorn.info")


def adp_coils_sc_sheet_parser(
    df: DataFrame, series: ADPProductSheet
) -> tuple[DataFrame]:
    product_rows, product_cols = ((16, 41), (2, 5))

    product = df.iloc[slice(*product_rows), slice(*product_cols)]
    product = product.dropna(how="all", axis=1).dropna(how="all", axis=0)
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
    result = product.melt(id_vars="key", var_name="suffix", value_name="price")
    result.dropna(inplace=True)
    result.loc[:, "key"] += "_" + result["suffix"]
    result = result[["key", "price"]]
    result["vendor_id"] = VendorId.ADP.value
    result["series"] = series.name
    result["price"] *= 100
    # return this so it can be unpacked
    return (result,)
