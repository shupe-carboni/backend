from datetime import datetime
from typing import Optional, Annotated
from enum import StrEnum, auto, Enum
from pydantic import BaseModel, ConfigDict, Field
from app.db import Session, DB_V2


class VendorId(StrEnum):
    ADP = "adp"
    ATCO = "atco"
    VYBOND = "vybond"
    FRIEDRICH = "friedrich"
    GLASFLOSS = "glasfloss"
    MILWAUKEE = "milwaukee"
    SOUTHWIRE = "southwire"
    TEST = "test"


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


class PriceTemplateSheet(StrEnum):
    CUSTOMER_PRICING = "Customer Pricing"
    CUSTOMER_PRICE_CATEGORY = "Customer Price Category"
    PRODUCT_CATEGORY_DISCOUNTS = "Product Category Discounts"
    PRODUCT_DISCOUNTS = "Product Discounts"


class PriceTemplateSheetColumn(StrEnum):
    PART_NUMBER = "Part Number"
    PRICING_CATEGORY = "Pricing Category"
    PRICE = "Price"
    CATEGORIES = "Categories"
    PRODUCT_CATEGORY = "Product Category"
    DISCOUNT = "Discount"
    CATEGORY_RANK = "Category Rank"


PriceTemplateSheetColumns = {
    PriceTemplateSheet.CUSTOMER_PRICING: [
        PriceTemplateSheetColumn.PART_NUMBER,
        PriceTemplateSheetColumn.PRICING_CATEGORY,
        PriceTemplateSheetColumn.PRICE,
    ],
    PriceTemplateSheet.CUSTOMER_PRICE_CATEGORY: [
        PriceTemplateSheetColumn.CATEGORIES,
    ],
    PriceTemplateSheet.PRODUCT_CATEGORY_DISCOUNTS: [
        PriceTemplateSheetColumn.PRODUCT_CATEGORY,
        PriceTemplateSheetColumn.CATEGORY_RANK,
        PriceTemplateSheetColumn.PRICING_CATEGORY,
        PriceTemplateSheetColumn.DISCOUNT,
    ],
    PriceTemplateSheet.PRODUCT_DISCOUNTS: [
        PriceTemplateSheetColumn.PART_NUMBER,
        PriceTemplateSheetColumn.DISCOUNT,
    ],
}

PosFloat = Annotated[float, Field(gt=0)]
PosInt = Annotated[int, Field(gt=0)]
Discount = Annotated[float, Field(gt=0, lt=1)]


class CustomerPrice(BaseModel):
    part_number: str
    pricing_category: str
    price: PosFloat

    def get_price_category_id(self, session: Session, vendor_id: VendorId) -> int:
        sql = """
            SELECT id
            FROM vendor_pricing_classes
            WHERE vendor_id = :vid
            AND name = :cat
        """
        params = dict(cat=self.pricing_category, vid=vendor_id.value)
        return DB_V2.execute(session, sql, params).scalar_one()

    def get_product_id(self, session: Session, vendor_id: VendorId) -> int:
        sql = """
            SELECT id
            FROM vendor_products
            WHERE vendor_product_identifier = :pid
            AND vendor_id = :vid
        """
        params = dict(pid=self.part_number, vid=vendor_id.value)
        return DB_V2.execute(session, sql, params).scalar_one()


class CustomerPriceCategory(BaseModel):
    category: str

    def get_price_category_id(self, session: Session, vendor_id: VendorId) -> int:
        sql = """
            SELECT id
            FROM vendor_pricing_classes
            WHERE vendor_id = :vid
            AND name = :cat
        """
        params = dict(cat=self.category, vid=vendor_id.value)
        return DB_V2.execute(session, sql, params).scalar_one()


class ProductCategoryDiscount(BaseModel):
    product_category: str
    category_rank: PosInt
    pricing_category: str
    discount: Discount

    def get_label_price_category_id(self, session: Session, vendor_id: VendorId) -> int:
        sql = """
            SELECT id
            FROM vendor_pricing_classes
            WHERE name = :price_cat
            AND vendor_id = :vid
        """
        params = dict(price_cat=self.pricing_category, vid=vendor_id.value)
        return DB_V2.execute(session, sql, params).scalar_one()

    def get_base_price_category_id(self, session: Session, vendor_id: VendorId) -> int:
        sql = """
            SELECT id
            FROM vendor_pricing_classes
            WHERE name = :price_cat
            AND vendor_id = :vid
        """
        params = dict(price_cat=VendorBasePriceClasses[vendor_id], vid=vendor_id.value)
        return DB_V2.execute(session, sql, params).scalar_one()

    def get_product_category_id(self, session: Session, vendor_id: VendorId) -> int:
        sql = """
            SELECT id
            FROM vendor_product_classes
            WHERE name = :product_cat
            AND rank = :cat_rank
            AND vendor_id = :vid
        """
        params = dict(
            product_cat=self.product_category,
            cat_rank=self.category_rank,
            vid=vendor_id.value,
        )
        return DB_V2.execute(session, sql, params).scalar_one()


class ProductDiscount(BaseModel):
    part_number: str
    discount: Discount

    def get_product_id(self, session: Session, vendor_id: VendorId) -> int:
        sql = """
            SELECT id
            FROM vendor_products
            WHERE vendor_product_identifier = :pid
            AND vendor_id = :vid
        """
        params = dict(pid=self.part_number, vid=vendor_id.value)
        return DB_V2.execute(session, sql, params).scalar_one()


PriceTemplateModels: dict[StrEnum, BaseModel] = {
    PriceTemplateSheet.CUSTOMER_PRICING: CustomerPrice,
    PriceTemplateSheet.CUSTOMER_PRICE_CATEGORY: CustomerPriceCategory,
    PriceTemplateSheet.PRODUCT_CATEGORY_DISCOUNTS: ProductCategoryDiscount,
    PriceTemplateSheet.PRODUCT_DISCOUNTS: ProductDiscount,
}

VendorBasePriceClasses: dict[StrEnum, str] = {
    VendorId.ADP: "ZERO_DISCOUNT_PRICE",
    VendorId.ATCO: "LIST_PRICE",
    VendorId.FRIEDRICH: None,
}
