import pandas as pd
import requests

FRACTION_CODES = {
    "A": 0.0625,
    "B": 0.1250,
    "C": 0.1875,
    "D": 0.2500,
    "E": 0.3125,
    "F": 0.3750,
    "G": 0.4375,
    "H": 0.5000,
    "J": 0.5625,
    "K": 0.6250,
    "L": 0.6875,
    "M": 0.7500,
    "N": 0.8125,
    "P": 0.8750,
    "R": 0.9375,
}

with open("/home/carboni/.local/share/shupe-carboni-backend-tui/token.txt") as file:
    token = dict(Authorization=file.read())

data = pd.read_csv("/home/carboni/Desktop/gls-nets-mapped.csv")

unique_pns = data[data["pn"].str.slice(0, 3).isin(("GDS", "GTA", "ZLP", "M11", "M13"))][
    "pn"
].unique()


def disect_model(m: str) -> tuple:
    m = m.replace("SP", "")
    dims_part = m[3:]
    exact = True if m[-1] == "E" else False
    if exact:
        dims_part = dims_part[:-1]
    if m[0:3] in ("GDS", "ZLP", "M11", "M13"):
        series = m[0:3]
    elif m[0:3] == "GTA":
        series = "GDS"
    if dims_part.endswith("0H"):
        depth = 0.5
        dims_part = dims_part[:-2]
    else:
        depth = int(dims_part[-1])
        dims_part = dims_part[:-1]
    if frac := FRACTION_CODES.get(dims_part[-1]):
        height = frac
        dims_part = dims_part[:-1]
    else:
        height = 0
    match len(dims_part):
        case 2:
            height += int(dims_part[-1])
            width = int(dims_part[-2])
        case 3 if dims_part[-2].isdecimal():
            height += int(dims_part[-2:])
            width = int(dims_part[0])
        case 3 if not dims_part[-2].isdecimal():
            height += int(dims_part[-1])
            width = int(dims_part[0]) + FRACTION_CODES[dims_part[-2]]
        case 4 if dims_part.isdecimal():
            height += int(dims_part[-2:])
            width = int(dims_part[:2])
        case 4 if not dims_part.isdecimal():
            height += int(dims_part[-2:])
            width = int(dims_part[0]) + FRACTION_CODES[dims_part[1]]
        case 5:
            height += int(dims_part[-2:])
            width = int(dims_part[0:2]) + FRACTION_CODES[dims_part[2]]
        case _:
            raise Exception(dims_part)
    return (series, width, height, depth, str(exact).lower())


def try_to_price(m: tuple) -> float:
    pn, s, w, h, d, e = m
    url = (
        "https://api.shupecarboni.com/glasfloss/model-lookup"
        f"?series={s}&width={w}&height={h}&depth={d}&exact={e}"
    )
    resp = requests.get(url, headers=token)
    if resp.status_code == 200:
        print(f"priced {pn}")
        return resp.json()["list-price"]
    else:
        print(f"failed on {pn}: {resp.text}")
        return 0


if __name__ == "__main__":
    model_parts = [tuple([pn, *disect_model(pn)]) for pn in unique_pns]
    results = [(m[0], try_to_price(m)) for m in model_parts]
    results_df = pd.DataFrame(results, columns=["pn", "price"])
    merged = data.merge(results_df, how="left", on="pn")
    merged.to_csv("/home/carboni/Desktop/gls-nets-w-list.csv", index=False)
