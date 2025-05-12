from logging import getLogger
from pandas import DataFrame
from app.admin.models import VendorId, ADPProductSheet

logger = getLogger("uvicorn.info")


def adp_ahs_amh_sheet_parser(
    df: DataFrame, series: ADPProductSheet
) -> tuple[DataFrame]:
    product_rows, product_cols = ((10, 39), (2, 5))
    product = df.iloc[slice(*product_rows), slice(*product_cols)]
    product = (
        product.dropna(how="all", axis=0).dropna(how="all", axis=1).iloc[:, [0, 2]]
    )
    product.columns = ["key", "price"]
    product["vendor_id"] = VendorId.ADP.value
    product["series"] = series.name
    product["price"] *= 100
    return (product,)
