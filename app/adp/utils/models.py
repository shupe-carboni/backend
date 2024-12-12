from enum import Enum, auto


class ParsingModes(Enum):
    ATTRS_ONLY = auto()
    BASE_PRICE = auto()
    BASE_PRICE_2024 = auto()
    CUSTOMER_PRICING = auto()
    CUSTOMER_PRICING_2024 = auto()
    DEVELOPER = auto()
