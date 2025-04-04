from enum import Enum, auto
from dataclasses import dataclass


class ParsingModes(Enum):
    ATTRS_ONLY = auto()
    BASE_PRICE = auto()
    BASE_PRICE_FUTURE = auto()
    CUSTOMER_PRICING = auto()
    CUSTOMER_PRICING_FUTURE = auto()
    DEVELOPER = auto()


class AttrType(Enum):
    NUMBER = int
    STRING = str


@dataclass
class ProgramFile:
    file_name: str
    file_data: bytes
