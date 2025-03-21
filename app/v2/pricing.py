from io import StringIO
from time import time
from typing import Callable, TypeAlias, Literal
from datetime import datetime
from logging import getLogger
from pandas import DataFrame, concat
from fastapi import HTTPException
from app.admin.models import VendorId, Pricing
from app.downloads import FileResponse
from app.db import DB_V2, Session
from app.admin import pricing_by_class, pricing_by_customer

logger = getLogger("uvicorn.info")


def flatten(pricing: dict) -> DataFrame:
    prices_formatted = []
    for price in pricing["data"]:
        price: dict
        product_info = {
            "part_id": price["product"]["part_id"],
            "description": price["product"]["description"],
        }
        product_attrs = {
            item["attr"]: item["value"] for item in price["product"]["attrs"]
        }
        product_categories = {
            f"category_{item['rank']}": item["name"]
            for item in price["product"]["categories"]
        }
        notes = {"notes": []}
        for item in price.get("notes", []):
            item: dict
            if item.get("id"):
                notes["notes"].append(f"{item['attr']}: {item['value']}")

        notes = {"notes": "\n".join(notes["notes"])}
        price_category = {"Price Category": price["category"]["name"]}
        df = DataFrame(
            [
                {
                    **product_info,
                    **price_category,
                    **product_categories,
                    **product_attrs,
                    "effective_date": price["effective_date"],
                    "price": price["price"],
                    "price_override": price.get("override", False),
                    **notes,
                    # don't include history for the file return
                    # "history": price[
                    #     "history"
                    # ],
                }
            ]
        )
        df["price"] /= 100
        prices_formatted.append(df)
    return concat(prices_formatted, ignore_index=True)


def transform(
    customer: dict,
    vendor_id: VendorId,
    data: Pricing | Callable,
    remove_cols: list[str] = None,
    pivot: bool = False,
) -> FileResponse:
    """
    Takes pricing and formats into a CSV for return as a file to the client.
    Although price history is included in the JSON response, the file
    contains only the current listing in the pricing tables, even if
    the effective_date is in the future

    TODO: set up a flag to prefer a historical price if given a date that falls
    between the current effective date and a historical date, most recent
    timestamp.

    """
    start = time()
    if isinstance(data, Callable):
        data = data()
    pricing_dict = data.model_dump(exclude_none=True)
    pricing_df = flatten(pricing_dict).drop(columns="price_override")
    if pivot:
        cols = list(pricing_df.columns)
        # remove the ones going away
        cols.remove("Price Category")
        cols.remove("price")
        anticipated_new_cols: list = pricing_df["Price Category"].unique().tolist()
        pricing_df = pricing_df.pivot(
            index=cols,
            columns="Price Category",
            values="price",
        ).reset_index()
        result = pricing_df[cols + anticipated_new_cols]
    else:
        result = pricing_df

    if remove_cols:
        try:
            result = result.drop(columns=remove_cols)
        except:
            pass
    result.columns = list(result.columns.str.replace("_", " ").str.title())
    buffer = StringIO()
    result.to_csv(buffer, index=False)
    buffer.seek(0)

    customer_name = customer["data"]["attributes"]["name"]
    vendor_name = vendor_id.value.title()
    today_ = str(datetime.now().today())
    filename = f"{customer_name} {vendor_name} Pricing {today_}"
    logger.info(f"transform: {time() - start}")
    return FileResponse(
        content=buffer,
        status_code=200,
        media_type="text/csv",
        filename=f"{filename}.csv",
    )


FetchMode: TypeAlias = Literal["both", "customer", "class"]


def fetch_pricing(
    session: Session,
    vendor_id: VendorId,
    customer_id: int,
    mode: FetchMode,
    override_key: str = None,
) -> Pricing:
    """
    Fetch either category-based pricing, customer-specific pricing, or both.
    In the case 'both' are fetched, customer-specific pricing may replace
    categorical price records. replace_on supplies a list of tuples containing key
    names to apply the filter with jointly (an AND relationship)
    """
    params = dict(vendor_id=vendor_id.value, customer_id=customer_id)
    start = time()
    try:
        match mode:
            case "both":
                customer_pricing = (
                    DB_V2.execute(session, pricing_by_customer, params=params)
                    .mappings()
                    .fetchall()
                )
                overrides = [e for e in customer_pricing if e["override"] == True]
                override_product_ids = set([e["product"]["id"] for e in overrides])
                customer_class_pricing = (
                    DB_V2.execute(session, pricing_by_class, params=params)
                    .mappings()
                    .fetchall()
                )
                pricing_list = []
                for price in customer_class_pricing:
                    prod_id = price["product"]["id"]
                    category = price["category"]["name"]
                    cond = prod_id in override_product_ids
                    if override_key:
                        cond = cond and category == override_key
                    if not cond:
                        pricing_list.append(price)

                pricing_list.extend(customer_pricing)
                pricing = Pricing(data=pricing_list)
            case "customer":
                customer_pricing = (
                    DB_V2.execute(session, pricing_by_customer, params=params)
                    .mappings()
                    .fetchall()
                )
                pricing = Pricing(data=customer_pricing)
            case "class":
                customer_class_pricing = (
                    DB_V2.execute(session, pricing_by_class, params=params)
                    .mappings()
                    .fetchall()
                )
                pricing = Pricing(data=customer_class_pricing)
    finally:
        session.close()
    logger.info(f"query execution: {time() - start}")
    if not pricing.data:
        raise HTTPException(404)
    return pricing
