from datetime import datetime
from typing import Any, Optional
from enum import StrEnum, auto
from pydantic import BaseModel


class VendorId(StrEnum):
    ADP = "adp"
    ATCO = "atco"
    BERRY = "berry"
    FRIEDRICH = "friedrich"
    GLASFLOSS = "glasfloss"
    MILWAUKEE = "milwaukee"
    SOUTHWIRE = "southwire"


class Customer(BaseModel):
    id: int
    name: str


class PriceCategory(BaseModel):
    id: int
    name: str


class ProductAttr(BaseModel):
    id: int
    attr: str
    type: str
    value: str


class PriceAttr(BaseModel):
    id: int
    attr: str
    type: str
    value: str


class ProductCategory(BaseModel):
    id: int
    name: str
    rank: int


class Product(BaseModel):
    id: int
    part_id: str
    description: Optional[str] = ""
    categories: list[ProductCategory]
    attrs: list[ProductAttr]


class PriceHistory(BaseModel):
    id: int
    price: int
    effective_date: datetime
    timestamp: datetime


class PriceItem(BaseModel):
    id: int
    override: Optional[bool] = None
    category: PriceCategory
    product: Product
    price: int
    effective_date: datetime
    history: list[PriceHistory]


class Pricing(BaseModel):
    data: list[PriceItem]


class FullPricing(BaseModel):
    customer_pricing: Optional[Pricing] = None
    category_pricing: Optional[Pricing] = None


class FullPricingWithLink(BaseModel):
    download_link: str
    pricing: Optional[FullPricing] = None


class ADPProductSheet(StrEnum):
    B = "B Series"
    CP_A1 = "CP Series A1"
    CP_A2L = "CP Series A2L"
    F = "F Series"
    S = "S Series"
    AMH = "mFurnace"
    HE = "HE Series"
    HH = "HH Series"
    MH = "M Series"
    V = "V Series"
    HD = "HD Series"
    SC = "SC Series"
    PARTS = "Parts"


class ADPCustomerRefSheet(StrEnum):
    ZERO_DISCOUNT = "Zero Disc"
    CUSTOMER_DISCOUNT = "Customer Discount"
    SPECIAL_NET = "Special Net"
    COMBINED = "Combined"
    OO = "OO"


class DBOps(StrEnum):
    SETUP = auto()
    POPULATE_TEMP = auto()
    UPDATE_EXISTING = auto()
    INSERT_NEW_PRODUCT = auto()
    INSERT_NEW_CUSTOMERS = auto()
    SETUP_ATTRS = auto()
    INSERT_NEW_PRODUCT_PRICING = auto()
    INSERT_NEW_DISCOUNTS = auto()
    UPDATE_CUSTOMER_PRICING = auto()
    REMOVE_MISSING = auto()
    TEARDOWN = auto()
