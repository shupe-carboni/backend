from io import StringIO
from time import time
from typing import Callable, TypeAlias, Literal
from datetime import datetime, timedelta
from logging import getLogger
from pandas import DataFrame, concat
from fastapi import HTTPException
from app.admin.models import VendorId, Pricing
from app.downloads import FileResponse
from app.db import DB_V2, Session
from app.db.sql import queries

logger = getLogger("uvicorn.info")


def flatten(pricing: dict, effective_date: datetime | None) -> DataFrame:
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

        # swap out the price and date signifying the current state
        # with either a historical or future date
        # Additionally, filter out future dated data that's in place of current
        def get_historical_price(price_: dict):
            if history := price_.get("history"):
                closest_ = history[0], effective_date - history[0]["effective_date"]
                for rec in history:
                    diff_ = effective_date - rec["effective_date"]
                    if timedelta(0) < diff_ < closest_[1]:
                        closest_ = rec, diff_

                (historic_price, _) = closest_
                price_["price"] = historic_price["price"]
                price_["effective_date"] = historic_price["effective_date"]
            return price_

        if not effective_date:
            effective_date = datetime.today()
        if effective_date >= datetime.today():
            if future := price.get("future"):
                if effective_date >= future["effective_date"]:
                    price["price"] = future["price"]
                    price["effective_date"] = future["effective_date"]
            if price["effective_date"] > effective_date:
                price = get_historical_price(price)
        elif effective_date == price["effective_date"]:
            # don't replace if the current price matches the given date
            pass
        else:
            price = get_historical_price(price)

        if price["effective_date"] > effective_date:
            # skip future pricing if not replaced by history
            continue

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
                }
            ]
        )
        df["price"] /= 100
        prices_formatted.append(df)
    if not prices_formatted:
        raise HTTPException(204)
    return concat(prices_formatted, ignore_index=True)


def transform(
    customer: dict,
    vendor_id: VendorId,
    data: Pricing | Callable,
    remove_cols: list[str] = None,
    pivot: bool = False,
    effective_date: datetime = None,
) -> FileResponse:
    """
    Takes pricing and formats into a CSV for return as a file to the client.
    """
    start = time()
    if isinstance(data, Callable):
        data = data()
    pricing_dict = data.model_dump(exclude_none=True)
    pricing_df = flatten(pricing_dict, effective_date=effective_date).drop(
        columns="price_override"
    )
    cols = list(pricing_df.columns)
    if pivot:
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
        # assumption is made that products are connected to AT LEAST one category to
        # sort on.
        guarantee_first = ["part_id", "description", "Price Category", "category_1"]
        guarantee_last = ["effective_date", "price", "notes"]
        other_cols = [
            col for col in cols if col not in set(guarantee_first + guarantee_last)
        ]
        result = pricing_df[guarantee_first + other_cols + guarantee_last].sort_values(
            by=(guarantee_first[-2:] + guarantee_first[:2])
        )

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
    file_date = (
        str(datetime.today().date()) if not effective_date else effective_date.date()
    )
    filename = f"{customer_name} {vendor_name} Pricing {file_date}"
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
                    DB_V2.execute(
                        session, queries.pricing_by_customer_json, params=params
                    )
                    .mappings()
                    .fetchall()
                )
                overrides = [e for e in customer_pricing if e["override"] == True]
                override_product_ids = set([e["product"]["id"] for e in overrides])
                customer_class_pricing = (
                    DB_V2.execute(session, queries.pricing_by_class_json, params=params)
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
                    DB_V2.execute(
                        session, queries.pricing_by_customer_json, params=params
                    )
                    .mappings()
                    .fetchall()
                )
                pricing = Pricing(data=customer_pricing)
            case "class":
                customer_class_pricing = (
                    DB_V2.execute(session, queries.pricing_by_class_json, params=params)
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


def calc_customer_pricing_from_product_class_discount(
    session: Session,
    product_class_discount_id: int,
    ref_pricing_class_id: int,
    new_pricing_class_id: int,
    effective_date: datetime,
    rounding_strategy: int,
    update_only: bool = False,
) -> None:
    """
    When a customer's product-class-based pricing discount is changed, pricing reflected
    in vendor_pricing_by_customer ought to be changed as well.

    The reference pricing class id is used to identify the pricing in pricing_by_class
    that can be used as the reference price against which to apply the new multiplier.
    Rounding strategy is passed to the SQL statment to shift the truncation introduced
    by ROUND, such that we can dynamically round to the nearest dollar or the nearest
    cent.
    """
    logger.info(f"Calculating pricing related to the modified product class discount")

    update_params = dict(
        pricing_class_id=ref_pricing_class_id,
        product_class_discount_id=product_class_discount_id,
        effective_date=effective_date,
        sig=rounding_strategy,
    )
    new_record_params = dict(
        ref_pricing_class_id=ref_pricing_class_id,
        new_price_class_id=new_pricing_class_id,
        product_class_discount_id=product_class_discount_id,
        effective_date=effective_date,
        sig=rounding_strategy,
    )
    try:
        DB_V2.execute(
            session, sql=queries.update_customer_pricing_current, params=update_params
        )
        DB_V2.execute(
            session, queries.update_customer_pricing_future, params=update_params
        )
        if not update_only:
            DB_V2.execute(
                session,
                sql=queries.new_customer_pricing_current,
                params=new_record_params,
            )
            DB_V2.execute(
                session,
                sql=queries.new_customer_pricing_future,
                params=new_record_params,
            )
    except Exception as e:
        logger.critical(e)
        session.rollback()
    else:
        logger.info("Update successful")
        session.commit()
    return
