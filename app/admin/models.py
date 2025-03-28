from datetime import datetime
from typing import Optional
from enum import StrEnum, auto, Enum
from pydantic import BaseModel, ConfigDict


class VendorId(StrEnum):
    ADP = "adp"
    ATCO = "atco"
    VYBOND = "vybond"
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
    id: Optional[int] = None
    attr: Optional[str] = None
    type: Optional[str] = None
    value: Optional[str] = None


class ProductCategory(BaseModel):
    id: int
    name: str
    rank: int


class Product(BaseModel):
    id: int
    part_id: str
    description: Optional[str] = ""
    categories: list[ProductCategory]
    attrs: Optional[list[ProductAttr]] = None


class PriceHistory(BaseModel):
    id: int
    price: int
    effective_date: datetime
    timestamp: datetime


class PriceFuture(BaseModel):
    price: int
    effective_date: datetime


class PriceItem(BaseModel):
    id: int
    override: Optional[bool] = None
    category: PriceCategory
    product: Product
    price: int
    effective_date: datetime
    history: list[PriceHistory]
    future: Optional[PriceFuture] = None
    notes: Optional[list[PriceAttr]] = None


class Pricing(BaseModel):
    data: list[PriceItem]


class FullPricingWithLink(BaseModel):
    download_link: str
    pricing: Optional[Pricing] = None


class ProductType(Enum):
    COILS = auto()
    AIR_HANDLERS = auto()
    PARTS = auto()


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


class ADPProductType(Enum):
    B = ProductType.AIR_HANDLERS
    CP_A1 = ProductType.AIR_HANDLERS
    CP_A2L = ProductType.AIR_HANDLERS
    F = ProductType.AIR_HANDLERS
    S = ProductType.AIR_HANDLERS
    AMH = ProductType.AIR_HANDLERS
    HE = ProductType.COILS
    HH = ProductType.COILS
    MH = ProductType.COILS
    V = ProductType.COILS
    HD = ProductType.COILS
    SC = ProductType.COILS
    PARTS = ProductType.PARTS


class ADPCustomerRefSheet(StrEnum):
    ZERO_DISCOUNT = "Zero Disc"
    CUSTOMER_DISCOUNT = "Customer Discount"
    SPECIAL_NET = "Special Net"
    COMBINED = "Combined"
    OO = "OO"


class ModelLookupADP(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_number: str
    customer_id: Optional[int] = 0
    future: Optional[bool] = False


class ModelLookupGlasfloss(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    series: Optional[str] = ""
    width: Optional[float] = 0
    height: Optional[float] = 0
    depth: Optional[float] = 0
    exact: Optional[bool] = False
    model_number: Optional[str] = ""
    customer_id: Optional[int] = 0
