from logging import getLogger
from pandas import DataFrame
from app.admin.models import VendorId, ADPProductSheet
from app.admin.price_sheet_parsers.adp import _adder_expansion

logger = getLogger("uvicorn.info")


def adp_ahs_f_sheet_parser(df: DataFrame, series: ADPProductSheet) -> list[DataFrame]:
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
    adders.iloc[:, 0] = adders.iloc[:, 0].str.replace(" ", "").str.lower()
    adders = adders.iloc[:, [0, 2]]
    adders.columns = ["description", "price"]
    adders_result = _adder_expansion.expand(__adder_name_mapping, adders, series)
    results = []
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
    return [*results, adders_result]
