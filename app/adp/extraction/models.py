import math
import copy
from random import random
import pandas as pd
import openpyxl as opxl
from fastapi import HTTPException
from datetime import datetime
from openpyxl.worksheet.worksheet import Worksheet
from app.auth import SecOp
from app.adp.adp_models import MODELS, S, Fields, ModelSeries
from app.adp.utils.validator import Validator
from app.db import Stage, Session, DB_V2
from app.adp.utils.models import ParsingModes
import warnings

warnings.simplefilter("ignore")

# NOTE in `extract_models` replace with in-mem collection of files passed in from api


class InvalidParsingMode(Exception): ...


class InvalidModelNumber(Exception): ...


def build_model_attributes(
    session: Session, adp_customer_id: int, model: str, parse_mode: ParsingModes
) -> pd.Series:
    record_series = parse_model_string(session, adp_customer_id, model, parse_mode)
    record_series["stage"] = Stage.PROPOSED.name
    record_series["effective_date"] = datetime.today().date()
    record_series = record_series.dropna()
    return record_series


def parse_model_string(
    session: Session, adp_customer_id: int, model: str, mode: ParsingModes
) -> pd.Series:

    match mode:
        case ParsingModes.BASE_PRICE_FUTURE | ParsingModes.CUSTOMER_PRICING_FUTURE:
            zero_disc_price_strat = mode
        case _:
            zero_disc_price_strat = ParsingModes.BASE_PRICE

    model_obj: ModelSeries = None
    for m in MODELS:
        if matched_model := Validator(session, model, m).is_model(
            zero_disc_price_strat
        ):
            model_obj = matched_model
    if not model_obj:
        raise HTTPException(
            400, f"Model number {model} is not a valid ADP model number"
        )
    record = model_obj.record()
    record_series = pd.Series(record)
    match mode:
        case ParsingModes.CUSTOMER_PRICING | ParsingModes.CUSTOMER_PRICING_FUTURE:
            record_series["customer_id"] = adp_customer_id
            priced_model = price_models_by_customer_discounts(
                session=session,
                model=record_series,
                adp_customer_id=adp_customer_id,
                price_mode=mode,
            )
            priced_model.pop("customer_id")
            return priced_model
        case ParsingModes.BASE_PRICE | ParsingModes.BASE_PRICE_FUTURE:
            return record_series
        case ParsingModes.ATTRS_ONLY:
            record_series.drop(index=Fields.ZERO_DISCOUNT_PRICE.value, inplace=True)
            return record_series
        case ParsingModes.DEVELOPER:
            # random pricing
            def to_field_style(value: str) -> str:
                return value.replace("-", "_").upper()

            price_cols = [
                Fields[to_field_style(price_col)]
                for price_col in SecOp.PRICE_COLUMNS
                if to_field_style(price_col) in Fields.__members__
            ]
            price_cols_in_record = set(price_cols) & set(record_series.index.to_list())
            for price_col in price_cols_in_record:
                record_series[price_col] = int(random() * 1000)
            return record_series
        case _:
            raise InvalidParsingMode


def extract_models_from_sheet(session: Session, sheet: Worksheet) -> list[ModelSeries]:
    """iterates over cell contents
    and uses Validator to see if the content appears to be
    a valid ADP part number.
    If content matches, add it to a list of model objects

    model_clean: ModelSeries

    Returns: list[ModelSeries]
    """
    models = list()
    for row in sheet:
        for col in range(sheet.max_column):
            try:
                val = row[col].value
            except IndexError:
                break
            for m in MODELS:
                if model_clean := Validator(session, val, m).is_model():
                    if isinstance(model_clean, S):
                        if model_clean.get("heat") == "XX":
                            for heat_option in ("05", "07", "10"):
                                model_variant = copy.deepcopy(model_clean)
                                model_variant["heat"] = heat_option
                                models.append(model_variant)
                        else:
                            models.append(model_clean)
                    else:
                        models.append(model_clean)
    return models


def extract_models_from_file(session: Session, file: str) -> set[ModelSeries]:
    wb = opxl.load_workbook(file)
    models = list()
    for sheet in wb.worksheets:
        models.extend(extract_models_from_sheet(session=session, sheet=sheet))
    return set(models)


def price_models_by_customer_discounts(
    session: Session,
    model: pd.Series,
    adp_customer_id: int,
    price_mode: ParsingModes = ParsingModes.CUSTOMER_PRICING,
) -> pd.Series:
    match price_mode:
        case ParsingModes.CUSTOMER_PRICING:
            mat_grp_disc_sql = """
                SELECT class.name AS mat_grp, discount, effective_date,
                    vendor_customer_id AS customer_id
                FROM vendor_product_class_discounts a
                JOIN vendor_product_classes as class on class.id = product_class_id
                WHERE vendor_customer_id = :adp_customer_id
                AND a.effective_date <= CURRENT_DATE
                AND a.deleted_at is null;
            """

            snps_sql = """
                SELECT vp.vendor_product_identifier AS model, vendor_customer_id AS customer_id,
                    discount
                FROM vendor_product_discounts AS a
                JOIN vendor_products AS vp ON vp.id = a.product_id
                WHERE vendor_customer_id = :adp_customer_id
                AND a.effective_date <= CURRENT_DATE
                AND a.deleted_at is null;
            """
        case ParsingModes.CUSTOMER_PRICING_FUTURE:
            mat_grp_disc_sql = """
                SELECT class.name AS mat_grp, future.discount, future.effective_date,
                    vendor_customer_id AS customer_id
                FROM vendor_product_class_discounts_future future
                JOIN vendor_product_class_discounts a
                    ON a.id = future.discount_id
                JOIN vendor_product_classes AS class on class.id = product_class_id
                WHERE vendor_customer_id = :adp_customer_id;
            """

            snps_sql = """
                SELECT vp.vendor_product_identifier AS model, vendor_customer_id AS customer_id,
                    future.discount
                FROM vendor_product_discounts_future AS future 
                JOIN vendor_product_discounts AS a
                    ON a.id = future.discount_id
                JOIN vendor_products AS vp ON vp.id = a.product_id
                WHERE vendor_customer_id = :adp_customer_id;
            """
    mat_grp_discounts = pd.DataFrame(
        DB_V2.execute(
            session=session,
            sql=mat_grp_disc_sql,
            params=dict(adp_customer_id=adp_customer_id),
        )
        .mappings()
        .fetchall()
    )
    snps = pd.DataFrame(
        DB_V2.execute(
            session=session,
            sql=snps_sql,
            params=dict(adp_customer_id=adp_customer_id),
        )
        .mappings()
        .fetchall()
    )

    no_disc_price = int(model["zero_discount_price"])
    mat_group: str = model["mpg"]
    if not mat_grp_discounts.empty:
        mat_group_disc: pd.Series = mat_grp_discounts.loc[
            (mat_grp_discounts[Fields.CUSTOMER_ID.value] == adp_customer_id)
            & (mat_grp_discounts["mat_grp"] == mat_group),
            "discount",
        ]
        mat_group_disc = mat_group_disc.item() if not mat_group_disc.empty else 0
    else:
        mat_group_disc = 0
    if not isinstance(model[Fields.PRIVATE_LABEL.value], str):
        model_num: str = model[Fields.MODEL_NUMBER.value]
    else:
        model_num: str = model[Fields.PRIVATE_LABEL.value]

    if not snps.empty:
        snp_disc: pd.Series = snps.loc[
            (snps[Fields.CUSTOMER_ID.value] == adp_customer_id)
            & (snps["model"] == model_num),
            "discount",
        ]
        snp_disc = snp_disc.item() if not snp_disc.empty else 0
    else:
        snp_disc = 0

    mat_group_price = no_disc_price * (1 - mat_group_disc / 100)
    mat_group_price = int(math.floor(mat_group_price + 0.5))
    mat_group_price = 0 if mat_group_price == no_disc_price else mat_group_price

    snp_price = no_disc_price * (1 - snp_disc / 100)
    snp_price = int(math.floor(snp_price + 0.5))
    snp_price = 0 if snp_price == no_disc_price else snp_price
    result = {
        Fields.MATERIAL_GROUP_DISCOUNT.value: (
            mat_group_disc if mat_group_disc else None
        ),
        Fields.MATERIAL_GROUP_NET_PRICE.value: (
            mat_group_price if mat_group_price else None
        ),
        Fields.SNP_DISCOUNT.value: snp_disc if snp_disc else None,
        Fields.SNP_PRICE.value: snp_price if snp_price else None,
        Fields.NET_PRICE.value: min(
            [price for price in (snp_price, mat_group_price, no_disc_price) if price]
        ),
    }
    model.update(result)
    return model
