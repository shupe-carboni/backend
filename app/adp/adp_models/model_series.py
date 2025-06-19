import re
from app.db import DB_V2, Session, Database, CACHE
from app.db.sql import queries
from pandas import DataFrame
from enum import StrEnum, auto
from typing import TypeAlias, Literal, Any


class NoBasePrice(Exception):
    def __init__(self, reason: str) -> None:
        self.reason = reason


class Cabinet(StrEnum):
    UNCASED = auto()
    EMBOSSED = auto()
    PAINTED = auto()


class Fields(StrEnum):
    CUSTOMER_ID = auto()
    ADP_ALIAS = auto()
    PROGRAM = auto()
    DESCRIPTION = auto()
    CATEGORY = auto()
    MODEL_NUMBER = auto()
    PRIVATE_LABEL = auto()
    TOP_LEVEL_CLASS = auto()
    MPG = auto()
    SERIES = auto()
    TONNAGE = auto()
    PALLET_QTY = auto()
    WIDTH = auto()
    DEPTH = auto()
    HEIGHT = auto()
    WEIGHT = auto()
    MOTOR = auto()
    METERING = auto()
    HEAT = auto()
    MIN_QTY = auto()
    CABINET = auto()
    CFM = auto()
    VOLTAGE = auto()
    LENGTH = auto()
    ZERO_DISCOUNT_PRICE = auto()
    STANDARD_PRICE = auto()
    PREFERRED_PRICE = auto()
    MATERIAL_GROUP_DISCOUNT = auto()
    MATERIAL_GROUP_NET_PRICE = auto()
    SNP_DISCOUNT = auto()
    SNP_PRICE = auto()
    NET_PRICE = auto()
    RATINGS_AC_TXV = auto()
    RATINGS_HP_TXV = auto()
    RATINGS_PISTON = auto()
    RATINGS_FIELD_TXV = auto()
    RATED = auto()
    STAGE = auto()
    FLEXCOIL_MODEL = "a2l_model"
    FLEXCOIL_PRICE = "a2l_price"
    SORT_ORDER = auto()
    PRICE_ID = auto()
    EFFECTIVE_DATE = auto()
    CONFIGURATION = auto()
    DOOR = auto()
    ACCESSORY_TYPE = auto()
    TOP = auto()

    def formatted(self):
        match self:
            case self.ADP_ALIAS:
                return self.name.lower()
            case self.FLEXCOIL_MODEL:
                return "A2L Model"
            case self.FLEXCOIL_PRICE:
                return "A2L Price"
            case self.SNP_PRICE | self.SNP_DISCOUNT:
                return "SNP" + result[3:]
            case self.RATINGS_AC_TXV:
                result = self.name.replace("_", " ").title()
                return result.replace("Ac Txv", "AC TXV")
            case self.RATINGS_HP_TXV:
                result = self.name.replace("_", " ").title()
                return result.replace("Hp Txv", "HP TXV")
            case self.RATINGS_FIELD_TXV:
                result = self.name.replace("_", " ").title()
                return result.replace("Field Txv", "Field TXV")
            case self.CFM:
                return "CFM"
            case _:
                return self.name.replace("_", " ").title()


PriceAdderCategory = Literal[
    "tonnage", "metering", "misc", "line_conn", "voltage", "RDS", "motor", "heat"
]
PriceByCategoryAndKey: TypeAlias = dict[PriceAdderCategory, dict[str, int]]


class ModelSeries:
    text_len: int
    regex: str
    session: Session

    class NoBasePrice(Exception): ...

    class KeyMode(StrEnum):
        EXACT = "exact"
        MEMBERSHIP = "membership"
        REGEX = "regex"
        FIRST_2_PARTS = "first_2_parts"
        ADDERS = "adders"

    coil_depth_mapping = {
        "A": 19.5,
        "C": 20.5,
        "D": 21.0,
        "E": 21.5,
    }

    paint_color_mapping = {
        "H": "Embossed",
        "V": "Embossed",
        "A": "Armstrong",
        "G": "ICP",
        "J": "Goodman/Amana",
        "N": "Nordyne",
        "P": "Carrier/Bryant/Payne",
        "C": "Carrier/Bryant/Payne",
        "R": "Rheem/Ruud",
        "T": "Trane/American Standard",
        "Y": "York/Luxaire/Coleman",
    }

    material_mapping = {
        "E": "Copper",
        "G": "Aluminum",
        "D": "Copper",
        "P": "Aluminum",
        "M": "Aluminum",
        "L": "Copper",
        "K": "Copper",
        "A": "Aluminum",
        "C": "Copper",
        "SS": "Aluminum",
        "TT": "Aluminum",
        "UU": "Aluminum",
        "BB": "Copper",
        "CC": "Copper",
        "DD": "Copper",
    }

    metering_mapping = {
        -1: "Piston (R-454B/R-32)",
        -2: "Piston (R-22)",
        1: "Piston (R-410a)",
        2: "Piston (R-22)",
        9: "Non-bleed HP-AC TXV (R-410a)",
        -9: "Non-bleed HP-AC TXV (R-410a)",
        "A": "Non-bleed HP-AC TXV (R-454B)",
        "B": "Non-bleed HP-AC TXV (R-32)",
        "C": "Bleed HP-AC TXV (R-454B)",
    }

    motors = {
        "C": "PSC motor",
        "P": "PSC motor",
        "E": "ECM motor",
        "V": "Variable-speed ECM motor",
    }

    kw_heat = {
        0: "no heat",
        3: "3 kW",
        5: "5 kW",
        6: "6 kW",
        7: "7.5 kW",
        8: "8 kW",
        10: "10 kW",
        12: "12.5 kW",
        15: "15 kW",
        20: "20 kW",
    }

    def __init__(
        self,
        session: Session,
        re_match: re.Match,
        db: Database,
        use_future: bool,
        customer_id: int,
    ):
        key_ = "adp_material_groups"
        cached = CACHE.get(key_)
        match cached:
            case DataFrame() if not cached.empty:
                self.mat_grps = cached
            case _ if cached:
                self.mat_grps = cached
            case _:
                self.mat_grps = DB_V2.load_df(session=session, table_name=key_)
                self.mat_grps.rename(
                    columns={"id": "mat_grp"}, inplace=True
                )  # HOT FIX FOR COLUMN NAME CHANGE IN DB
                CACHE.add_or_update(key=key_, new_data=self.mat_grps)

        self.attributes = re_match.groupdict()
        self.session = session
        self.db = db
        self.use_future = use_future
        self.customer_id = customer_id
        if self.use_future:
            self.pricing_sql = queries.product_series_pricing_reach_into_future
        else:
            self.pricing_sql = queries.product_series_pricing_with_override_dynamic

    def __str__(self) -> str:
        return "".join(self.attributes.values()).strip()

    def __getitem__(self, key):
        return self.attributes.get(key)

    def __setitem__(self, key, value):
        self.attributes[key] = value

    def __delitem__(self, key):
        del self.attributes[key]

    def get(self, key):
        return self.__getitem__(key)

    def __series_name__(self):
        return self.__class__.__name__

    def calc_zero_disc_price(self) -> int:
        pass

    def category(self) -> str:
        """Use model series and features to describe
        a natural grouping in which it would appear
        in a customer program"""
        pass

    def record(self) -> dict[StrEnum, Any]:
        """Initialize an empty record to be updated by the subclass"""
        return {field.value: None for field in Fields.__members__.values()}

    def regex_match(self, pattern: str, ref: str = None) -> bool:
        reference = str(self) if not ref else ref
        try:
            print("herheree")
            return re.search(pattern, reference) is not None
        except re.error:
            return False

    def get_adders(self) -> PriceByCategoryAndKey:
        key_ = f"adp_series_{self.__series_name__()}"
        params = dict(
            series=self.__series_name__(),
            vendor_id="adp",
            key_mode="adders",
            key_param=[""],
            customer_id=self.customer_id,
        )
        adders_: list[dict[str, str | int]] = (
            self.db.execute(session=self.session, sql=self.pricing_sql, params=params)
            .mappings()
            .all()
        )
        adders = dict()
        for adder in adders_:
            # adder_type is a container in case the type name itself has underscores
            _, *adder_type, adder_key = adder["key"].split("_")
            adder_type = "_".join(adder_type)
            adders.setdefault(adder_type, {})
            adders[adder_type] |= {adder_key: adder["effective_price"]}
        # CACHE.add_or_update(key_, adders)
        return adders
