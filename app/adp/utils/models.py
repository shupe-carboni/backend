from enum import Enum, auto


class ParsingModes(Enum):
    ATTRS_ONLY = auto()
    BASE_PRICE = auto()
    BASE_PRICE_FUTURE = auto()
    CUSTOMER_PRICING = auto()
    CUSTOMER_PRICING_FUTURE = auto()
    DEVELOPER = auto()
