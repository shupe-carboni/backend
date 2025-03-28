from pandas import DataFrame, concat
from app.admin.models import VendorId, ADPProductSheet


def adp_ahs_cp_series_handler(
    df: DataFrame, sheet: ADPProductSheet
) -> tuple[DataFrame]:
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
    return (result,)
