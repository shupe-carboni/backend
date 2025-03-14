from datetime import datetime
from typing import Any, Optional
from enum import StrEnum
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
    M_FURNACE = "mFurnace"


class ADPSeries(StrEnum):
    B = "B"
    CP_A1 = "CP"
    CP_A2L = "CP"
    F = "F"
    S = "S"
    M_FURNACE = "AMH"
