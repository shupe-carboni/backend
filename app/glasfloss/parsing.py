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
    carton_weight: Optional[str] = Field(default=None, alias="carton-weight")
    list_price: float = Field(alias="list-price")
    multiplier: float = Field(alias="effective-multiplier")
    customer_multiplier: float = Field(alias="customer-multiplier")
    net_price: float = Field(alias="net-price")
    net_price_broken_case: Optional[float] = Field(
        default=None, alias="net-price-broken-case"
    )
    effective_date: datetime = Field(alias="effective-date")


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
        self.customer_multiplier = 1
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
                    self.multiplier = 1.3
                    self.double = True
                self.broken_case_multiplier = 1.4
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
                self.broken_case_multiplier = 1.4
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
                self.broken_case_multiplier = 1.4
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
                self.broken_case_multiplier = 1.4
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
                self.broken_case_multiplier = 1.4
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

    def calculate_pricing(self, customer_id: int = 0) -> "FilterModel":
        """
        Look for the model as a standard model first
        If it's not a standard model, use the calculation methods.
        Return the list price and broken pallet pricing.

        If a customer_id is passed, also return the customer's multiplier and net price
        """

        def set_multipliers(standard: bool) -> None:
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
            if not customer_id:
                return
            match self.model_type:
                case ModelType.GDS if standard:
                    if int(self.depth) in (1, 2):
                        rank_3_name = f"{int(self.depth)} GDS DISPOSABLE"
                case ModelType.GDS if not standard:
                    rank_3_name = "GTA MADE-TO-ORDER DISPOSABLE"
                case ModelType.HVP if standard:
                    if int(self.depth) in (1, 2, 4):
                        rank_3_name = f"HV {int(self.depth)} PLEATS"
                case ModelType.HVP if not standard:
                    rank_3_name = f"HV - MADE-TO-ORDER"
                case ModelType.ZLP if standard:
                    if int(self.depth) in (1, 2, 4):
                        rank_3_name = f"ZL {int(self.depth)} PLEAT"
                case ModelType.ZLP if not standard:
                    if int(self.depth) in (1, 2, 4):
                        rank_3_name = f"{int(self.depth)} ZL MADE-TO-ORDER"
                    elif int(self.depth) == 6:
                        rank_3_name = f"4 ZL MADE-TO-ORDER"
                case ModelType.M11 if standard:
                    if int(self.depth) in (1, 2, 4):
                        rank_3_name = f"MR-11 STANDARD SIZE {int(self.depth)}"
                case ModelType.M11 if not standard:
                    rank_3_name = f"MR-11 PLEAT - MADE-TO-ORDER"
                case ModelType.M13 if standard:
                    if int(self.depth) in (1, 2, 4):
                        rank_3_name = f"MR-13 STANDARD SIZE {int(self.depth)}"
                case ModelType.M13 if not standard:
                    rank_3_name = f"MR-13 PLEAT - MADE-TO-ORDER"

            customer_product_multiplier = DB_V2.execute(
                self.session,
                sql=customer_product_multiplier_sql,
                params=dict(
                    model_number=str(self.model_number), customer_id=customer_id
                ),
            ).one_or_none()
            if customer_product_multiplier:
                multiplier, self.effective_date = customer_product_multiplier
                self.customer_multiplier = multiplier
                self.multiplier *= multiplier
            else:
                customer_class_multiplier = DB_V2.execute(
                    self.session,
                    sql=customer_product_class_multiplier_sql,
                    params=dict(rank_3_name=rank_3_name, customer_id=customer_id),
                ).one_or_none()
                if customer_class_multiplier:
                    multiplier, self.effective_date = customer_class_multiplier
                    self.customer_multiplier = multiplier
                    self.multiplier *= multiplier
            return

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

        standard_filter = DB_V2.execute(
            session=self.session,
            sql=standard_filter_sql,
            params=dict(
                model_number=str(self.model_number),
                types=tuple([v.value for v in SecondOrderCategory]),
            ),
        ).one_or_none()

        if standard_filter:
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
            self.list_price = price
            self.effective_date = effective_date
            set_multipliers(standard=True)
        else:
            depth_placeholder = self.depth if 4 >= self.depth else 4
            mto_lookup_sql = """
                WITH glasfloss_pricing_mto AS (
                    SELECT 
                        id,
                        series,
                        split_part(key,'_',1) as size_type,
                        split_part(key,'_',2) as part_number,
                        split_part(key,'_',3)::float / 100 as depth,
                        split_part(key,'_',4)::int as upper_bnd_face_area,
                        price
                    FROM vendor_product_series_pricing
                    WHERE vendor_id = 'glasfloss'
                )
                SELECT price, part_number
                FROM glasfloss_pricing_mto
                WHERE series = :series
                AND size_type = :size_type
                AND depth = :depth
                AND upper_bnd_face_area = (
                    SELECT MIN(upper_bnd_face_area)
                    FROM glasfloss_pricing_mto
                    WHERE upper_bnd_face_area >= :face_area
                    AND series = :series
                    AND size_type = :size_type
                );
            """
            match self.model_type:
                case ModelType.GDS:
                    size_type = "DOUBLE" if self.double else "SINGLE"
                    face_area = self.face_area
                    adjustment = 1
                case (
                    ModelType.ZLP | ModelType.HVP | ModelType.M11 | ModelType.M13
                ) if self.double:
                    size_type = "SINGLE"
                    face_area = self.face_area / 2
                    adjustment = 2
                case (
                    ModelType.ZLP | ModelType.HVP | ModelType.M11 | ModelType.M13
                ) if not self.double:
                    size_type = "SINGLE"
                    face_area = self.face_area
                    adjustment = 1
            result = DB_V2.execute(
                self.session,
                mto_lookup_sql,
                params=dict(
                    series=self.model_series,
                    size_type=size_type,
                    depth=depth_placeholder,
                    face_area=face_area,
                ),
            ).one()
            (self.list_price, new_prefix) = result
            self.list_price *= adjustment
            self.model_number.prefix = new_prefix[:-2]
            self.qty_per_case = 12
            self.carton_weight = None
            self.effective_date = datetime.today()
            set_multipliers(standard=False)

        self.net_price = self.list_price * self.multiplier
        self.net_price_broken_case = self.net_price * self.broken_case_multiplier
        self.calculated = True
        return self

    def to_obj(self) -> FilterBuilt:
        if not self.calculated:
            raise Exception(
                "Apply method .calculate_pricing() before returning the "
                "built filter object."
            )
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
            list_price=Decimal(self.list_price / 100).quantize(
                ROUNDING_SIG, rounding=ROUND_HALF_UP
            ),
            multiplier=self.multiplier,
            customer_multiplier=self.customer_multiplier,
            net_price=Decimal(self.net_price / 100).quantize(
                ROUNDING_SIG, rounding=ROUND_HALF_UP
            ),
            net_price_broken_case=Decimal(self.net_price_broken_case / 100).quantize(
                ROUNDING_SIG, rounding=ROUND_HALF_UP
            ),
            effective_date=self.effective_date,
        )
        return FilterBuilt(**ret)
