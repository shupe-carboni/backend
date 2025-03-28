from pandas import DataFrame
from app.admin.models import VendorId, ADPProductSheet


def expand(
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
