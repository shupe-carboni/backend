from logging import getLogger
from pandas import DataFrame, Series, concat
from app.admin.models import VendorId, ADPProductSheet

logger = getLogger("uvicorn.info")


def adp_ahs_b_sheet_parser(df: DataFrame, series: ADPProductSheet) -> tuple[DataFrame]:
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
        [(k, v) for k, v_list in __adder_name_mapping.items() for v in v_list],
        columns=["description", "key"],
    )
    adders_result = adders.merge(
        adder_name_mapping,
        on="description",
        how="left",
    ).explode("key")
    adders_result["key"] = adders_result["key"].fillna(adders_result["description"])
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
        result["tonnage"].astype(str) + "_" + result["slab"] + "_" + result["suffix"]
    )
    result = concat([result[["key", "price"]], adders_result])
    result["vendor_id"] = VendorId.ADP.value
    result["series"] = series.name
    result["price"] *= 100
    return (result,)
