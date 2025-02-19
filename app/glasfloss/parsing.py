from typing import Any, Optional
from enum import StrEnum
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, Field, ConfigDict

from app.db import DB_V2, Session

ROUNDING_SIG = Decimal("1.00")


class ModelType(StrEnum):
    GDS = "GDS DISPOSABLE FILTERS"
    ZLP = "Z-LINE STANDARD PLEAT FILTERS"
    HVP = "Z-LINE HV PLEAT FILTERS"
    M11 = "Z-LINE MERV 11 PLEAT FILTERS"
    M13 = "Z-LINE MERV 13 PLEAT FILTERS"


class SecondOrderCategory(StrEnum):
    SEMI_STANDARD = "SEMI-STANDARD"
    STANDARD = "STANDARD"
    GEO_THERMAL_REPLACEMENT = "GEO-THERMAL_REPLACEMENT"

    """
    How do I expect the data to be coming in? Will it be a full model number
    (expecting the front end to do the model number construction from parts)?
    Or will I get certain pieces, constructing it in the backend? 

    ADP's approach uses a full model number coming from the client and parses it.
    This has made bulk uploads from the client very easy, but I have to verify the 
    model numbers in the backend (which I don't even do fully to catch bad ones).

    I could take parts of it, like the model type/series and dimensions, and build the 
    model and such from there. I'm thinking that may be the way to go for this.

    i.e. ZLP, 10.5, 21, 2, true (for "exact")
    """


@dataclass
class Filter:
    width: float
    height: float
    depth: float
    exact: bool


class FilterModelNumber:
    def __init__(
        self,
        prefix: str,
        width: int,
        height: int,
        depth: int,
        width_frac: Optional[str] = None,
        height_frac: Optional[str] = None,
        depth_frac: Optional[str] = None,
        exact: Optional[str] = None,
    ) -> None:
        self.prefix = prefix
        self.width = width
        self.height = height
        self.depth = depth
        self.width_frac = width_frac
        self.height_frac = height_frac
        self.depth_frac = depth_frac
        self.exact = exact

    def __str__(self) -> str:
        return "".join(
            [
                self.prefix,
                str(self.width),
                self.width_frac,
                str(self.height),
                self.height_frac,
                str(self.depth),
                self.depth_frac,
                self.exact,
            ]
        )


class FilterBuilt(BaseModel):
    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())
    model_number: str = Field(alias="model-number")
    width: float = Field(alias="width")
    height: float = Field(alias="height")
    depth: float = Field(alias="depth")
    exact: bool = Field(alias="exact")
    face_area: float = Field(alias="face-area")
    double_size: bool = Field(alias="double-size")
    qty_per_case: int = Field(alias="qty-per-case")
    carton_weight: str = Field(alias="carton-weight")
    list_price: float = Field(alias="list-price")
    multiplier: float = Field(alias="multiplier")
    net_price: float = Field(alias="net-price")
    net_price_broken_pallet: Optional[float] = Field(
        default=None, alias="net-price-broken-pallet"
    )
    effective_date: datetime = Field(alias="effective-date")


@dataclass
class Pricing:
    list_price: int
    multiplier: float
    net_price: int
    net_price_broken_pallet: int
    effective_date: datetime


FRACTION_CODES = {
    625: "A",
    1250: "B",
    1875: "C",
    2500: "D",
    3125: "E",
    3750: "F",
    4375: "G",
    5000: "H",
    5625: "J",
    6250: "K",
    6875: "L",
    7500: "M",
    8125: "N",
    8750: "P",
    9375: "R",
}
ALLOWED_DEPTHS = {
    ModelType.GDS: [0.5, 1, 2],
    ModelType.ZLP: [1, 2, 4],
    ModelType.HVP: [1, 2, 4, 6],
    ModelType.M11: [1, 2, 4, 6],
    ModelType.M13: [1, 2, 4, 6],
}


def convert_to_letter_code(dim: float) -> str:
    significance: int = 10**4
    return FRACTION_CODES[int((dim * significance) % significance)]


def convert_attr_type(type_: str, value: str) -> Any:
    match type_:
        case "NUMBER":
            result = float(value)
            if not result % 1:
                return int(result)
            else:
                return result
        case "STRING":
            return value
        case "BOOLEN":
            if value.lower().strip() == "true":
                return True
            else:
                return False


class FilterModel:
    def __init__(self, session: Session, model_type: ModelType, filter_dims: Filter):
        if not all((filter_dims.depth, filter_dims.height, filter_dims.width)):
            raise Exception("Invalid model dimensions given")
        self.session = session
        self.width = filter_dims.width
        self.height = filter_dims.height
        self.depth = filter_dims.depth
        self.exact = filter_dims.exact
        self.face_area = self.width * self.height
        self.model_type = model_type
        self.model_series = model_type.name
        self.desc = model_type.value
        self.exact = filter_dims.exact
        self.exact_nomen = "E" if filter_dims.exact else ""
        self.multiplier = 1
        self.calculated = False

        width_part = int(self.width)
        height_part = int(self.height)
        depth_part = int(self.depth)
        try:
            if width_part != self.width:
                width_frac = convert_to_letter_code(self.width)
            else:
                width_frac = ""
            if height_part != self.height:
                height_frac = convert_to_letter_code(self.height)
            else:
                height_frac = ""
            if depth_part != self.depth:
                depth_frac = convert_to_letter_code(self.depth)
            else:
                depth_frac = ""
        except KeyError as e:
            raise Exception("Invalid model dimensions given")

        match model_type:
            case ModelType.GDS:
                invalid_depth = self.depth not in ALLOWED_DEPTHS[ModelType.GDS]
                below_min = self.width < 4 and self.height < 4
                above_max = self.width > 96 or self.height > 96
                exception_case = invalid_depth or below_min or above_max
                if exception_case:
                    raise Exception("Invalid model dimensions given")
                if (4 <= self.width <= 25) and (4 <= self.height <= 36):
                    # the overlapping case, 4x36, defaults to 'single'
                    self.double = False
                elif (4 <= self.width <= 25) and (36 <= self.height <= 72):
                    self.double = True
                elif (4 <= self.width <= 36) and (36 <= self.height <= 54):
                    self.double = True
                elif (36 < self.width) and (54 < self.height):
                    self.double = True
                    self.multiplier = 1.3
                elif (72 < self.width <= 78) or (72 < self.height <= 78):
                    self.double = True
                    self.multiplier = 1.3
                elif (78 < self.width <= 96) or (78 < self.height <= 96):
                    self.double = True
                    self.multiplier = 1.5
                else:
                    self.double = False
            case ModelType.ZLP:
                invalid_depth = self.depth not in ALLOWED_DEPTHS[ModelType.ZLP]
                below_min = self.width < 4 and self.height < 4
                above_max = self.width > 96 or self.height > 96
                exception_case = invalid_depth or below_min or above_max
                if exception_case:
                    raise Exception("Invalid model dimensions given")
                if self.width > 28 and self.height > 28:
                    self.double = True
                elif self.width > 35 or self.height > 35:
                    self.double = True
                else:
                    self.double = False
            case ModelType.HVP:
                invalid_depth = self.depth not in ALLOWED_DEPTHS[ModelType.HVP]
                below_min = self.width < 4 and self.height < 4
                above_max = self.width > 96 or self.height > 96
                exception_case = invalid_depth or below_min or above_max
                if exception_case:
                    raise Exception("Invalid model dimensions given")
                if self.width > 28 and self.height > 28:
                    self.double = True
                elif self.width > 35 or self.height > 35:
                    self.double = True
                else:
                    self.double = False
                if depth_part == 6:
                    self.multiplier = 1.55
            case ModelType.M11:
                invalid_depth = self.depth not in ALLOWED_DEPTHS[ModelType.M11]
                below_min = self.width < 4 and self.height < 4
                above_max = self.width > 96 or self.height > 96
                exception_case = invalid_depth or below_min or above_max
                if exception_case:
                    raise Exception("Invalid model dimensions given")
                if self.width > 24.75 and self.height > 24.75:
                    self.double = True
                elif self.width > 35 or self.height > 35:
                    self.double = True
                else:
                    self.double = False
                if depth_part == 6:
                    self.multiplier = 1.55
            case ModelType.M13:
                invalid_depth = self.depth not in ALLOWED_DEPTHS[ModelType.M13]
                below_min = self.width < 4 and self.height < 4
                above_max = self.width > 96 or self.height > 96
                exception_case = invalid_depth or below_min or above_max
                if exception_case:
                    raise Exception("Invalid model dimensions given")
                if self.width > 24.75 and self.height > 24.75:
                    self.double = True
                elif self.width > 35 or self.height > 35:
                    self.double = True
                else:
                    self.double = False
                if depth_part == 6:
                    self.multiplier = 1.55
            case _:
                raise Exception("Invalid Model Type")

        self.model_number = FilterModelNumber(
            self.model_series,
            width=width_part,
            width_frac=width_frac,
            height=height_part,
            height_frac=height_frac,
            depth=depth_part,
            depth_frac=depth_frac,
            exact=self.exact_nomen,
        )
        return

    def calculate_pricing(self, customer_id: int) -> "FilterModel":
        """
        Look for the model as a standard model first
        If it's not a standard model, use the calculation methods.
        Return the list price and broken pallet pricing.

        If a customer_id is passed, also return the customer's multiplier and net price
        """
        standard_filter_sql = """
            SELECT product_id, price, effective_date
            FROM vendor_pricing_by_class
            WHERE exists (
                SELECT 1 
                FROM vendor_products a 
                JOIN vendor_product_to_class_mapping b ON b.product_id = a.id 
                JOIN vendor_product_classes c ON c.id = b.product_class_id 
                WHERE c.name in :types 
                AND a.vendor_id = 'glasfloss' 
                AND a.id = vendor_pricing_by_class.product_id
                AND a.vendor_product_identifier = :model_number);
        """
        customer_product_class_multiplier_sql = """
            SELECT (1-discount) as multiplier, effective_date
            FROM vendor_product_class_discounts a
            WHERE EXISTS (
                SELECT 1
                FROM vendor_customers b
                WHERE a.vendor_customer_id = b.id
                AND b.vendor_id = 'glasfloss'
            )
            AND EXISTS (
                SELECT 1
                FROM vendor_product_classes c
                WHERE c.rank = 3
                AND c.name = :rank_3_name
                AND c.vendor_id = 'glasfloss'
                AND c.id = a.product_class_id
            )
            AND a.vendor_customer_id = :customer_id;
        """
        customer_product_multiplier_sql = """
            SELECT (1-discount) as multiplier, effective_date
            FROM vendor_product_discounts a
            WHERE EXISTS (
                SELECT 1
                FROM vendor_customers b
                WHERE a.vendor_customer_id = b.id
                AND b.vendor_id = 'glasfloss'
            )
            AND EXISTS (
                SELECT 1
                FROM vendor_products c
                WHERE c.vendor_product_identifier = :model_number
                AND c.vendor_id = 'glasfloss'
                AND c.id = a.product_id
            )
            AND a.vendor_customer_id = :customer_id;
        """
        standard_filter = DB_V2.execute(
            session=self.session,
            sql=standard_filter_sql,
            params=dict(
                model_number=str(self.model_number),
                types=tuple([v.value for v in SecondOrderCategory]),
            ),
        ).one_or_none()

        if standard_filter:
            self.prefix = self.model_series
            product_id, price, effective_date = standard_filter
            filter_features_sql = """
                SELECT attr, type, value
                FROM vendor_product_attrs
                WHERE vendor_product_id = :product_id;
            """
            filter_features = DB_V2.execute(
                self.session,
                sql=filter_features_sql,
                params=dict(product_id=product_id),
            ).fetchall()
            attrs = {
                attr: convert_attr_type(type, value)
                for attr, type, value in filter_features
            }
            self.qty_per_case = attrs.get("qty_per_case")
            self.carton_weight = attrs.get("carton_weight")
            self.list_price = price / 100
            self.effective_date = effective_date

            if customer_id:
                match self.model_type:
                    case ModelType.GDS:
                        if int(self.depth) in (1, 2):
                            rank_3_name = f"{int(self.depth)} GDS DISPOSABLE"
                    case ModelType.HVP:
                        if int(self.depth) in (1, 2, 4):
                            rank_3_name = f"HV {int(self.depth)} PLEATS"
                    case ModelType.ZLP:
                        if int(self.depth) in (1, 2, 4):
                            rank_3_name = f"ZL {int(self.depth)} PLEAT"
                    case ModelType.M11:
                        if int(self.depth) in (1, 2, 4):
                            rank_3_name = f"MR-11 STANDARD SIZE {int(self.depth)}"
                    case ModelType.M13:
                        if int(self.depth) in (1, 2, 4):
                            rank_3_name = f"MR-13 STANDARD SIZE {int(self.depth)}"

                customer_multiplier = DB_V2.execute(
                    self.session,
                    sql=customer_product_class_multiplier_sql,
                    params=dict(rank_3_name=rank_3_name, customer_id=customer_id),
                ).one_or_none()
                if customer_multiplier:
                    multiplier, self.effective_date = customer_multiplier
                    self.multiplier *= multiplier
            self.net_price = self.list_price * self.multiplier
        else:
            self.prefix = self.model_series
            self.qty_per_case = 0
            self.carton_weight = ""
            self.list_price = 0
            self.effective_date = datetime.today()
            self.net_price = 0

        self.calculated = True
        return self

    def to_obj(self) -> FilterBuilt:
        if not self.calculated:
            raise Exception(
                "Apply method .calculate_pricing() before returning the "
                "built filter object."
            )
        self.model_number.prefix = self.prefix
        ret = dict(
            model_number=str(self.model_number),
            width=self.width,
            height=self.height,
            depth=self.depth,
            exact=self.exact,
            face_area=self.face_area,
            double_size=self.double,
            qty_per_case=self.qty_per_case,
            carton_weight=self.carton_weight,
            list_price=self.list_price,
            multiplier=self.multiplier,
            net_price=Decimal(self.net_price).quantize(
                ROUNDING_SIG, rounding=ROUND_HALF_UP
            ),
            net_price_broken_pallet=None,
            effective_date=self.effective_date,
        )
        return FilterBuilt(**ret)
