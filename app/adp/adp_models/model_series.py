import re
from app.db import ADP_DB
from enum import Enum, StrEnum, auto

session = next(ADP_DB.get_db())

class Cabinet(Enum):
    UNCASED = 0
    EMBOSSED = 1
    PAINTED = 2

class Fields(StrEnum):
    CUSTOMER_ID = auto()
    ADP_ALIAS = auto()
    PROGRAM = auto()
    CATEGORY = auto()
    MODEL_NUMBER = auto()
    PRIVATE_LABEL = auto()
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
    LENGTH = auto()
    ZERO_DISCOUNT_PRICE = auto()
    MATERIAL_GROUP_DISCOUNT = auto()
    MATERIAL_GROUP_NET_PRICE = auto()
    SNP_DISCOUNT = auto()
    SNP_PRICE = auto()
    NET_PRICE = auto()
    RATINGS_AC_TXV = auto()
    RATINGS_HP_TXV = auto()
    RATINGS_PISTON = auto()
    RATINGS_FIELD_TXV = auto()

    def formatted(self):
        if self.name == 'ADP_ALIAS':
            return self.name.lower()
        result = self.name.replace('_', ' ').title()
        if result.startswith('Snp'):
            result = 'SNP' + result[3:]
        elif result.endswith('Ac Txv'):
            result = result.replace('Ac Txv', 'AC TXV')
        elif result.endswith('Hp Txv'):
            result = result.replace('Hp Txv', 'HP TXV')
        elif result.endswith('Field Txv'):
            result = result.replace('Field Txv', 'Field TXV')
        return result


class ModelSeries:
    text_len: int
    regex: str

    mat_grps = ADP_DB.load_df(session=session, table_name='material_groups')
    coil_depth_mapping = {
        'A': 'uncased',
        'C': 20.5,
        'D': 21.0,
        'E': 21.5,
    }

    paint_color_mapping = {
        'H': 'Embossed',
        'V': 'Emboseed',
        'A': 'Armstrong',
        'G': 'ICP',
        'J': 'Goodman/Amana',
        'N': 'Nordyne',
        'P': 'Carrier/Bryant/Payne',
        'C': 'Carrier/Bryant/Payne',
        'R': 'Rheem/Ruud',
        'T': 'Trane/American Standard',
        'Y': 'York/Luxaire/Coleman',
    }

    material_mapping = {
        'E': 'Copper',
        'G': 'Aluminum',
        'D': 'Copper',
        'P': 'Aluminum',
        'M': 'Aluminum',
        'L': 'Copper',
        'K': 'Copper',
        'A': 'Aluminum',
        'C': 'Copper',
        'SS': 'Aluminum',
        'TT': 'Aluminum',
        'UU': 'Aluminum',
        'BB': 'Copper',
        'CC': 'Copper',
        'DD': 'Copper'
    }

    metering_mapping = {
        1: 'Piston (R-410a)',
        9: 'Non-bleed HP-AC TXV (R-410a)',
    }

    motors = {
        'C': 'PSC motor',
        'P': 'PSC motor',
        'E': 'ECM motor',
        'V': 'Variable-speed ECM motor'
    }

    kw_heat = {
        0: 'no heat',
        3: '3 kW',
        5: '5 kW',
        6: '6 kW',
        7: '7.5 kW',
        8: '8 kW',
        10: '10 kW',
        15: '15 kW',
        20: '20 kW',
    }

    def __init__(self, re_match: re.Match):
        self.attributes = re_match.groupdict()
    
    def __str__(self) -> str:
        return "".join(self.attributes.values())

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
    
    def record(self) -> dict:
        return {
            Fields.CATEGORY.value: None,
            Fields.MODEL_NUMBER.value: None,
            Fields.PRIVATE_LABEL.value: None,
            Fields.MPG.value: None,
            Fields.SERIES.value: None,
            Fields.TONNAGE.value: None,
            Fields.PALLET_QTY.value: None,
            Fields.MIN_QTY.value: None,
            Fields.WIDTH.value: None,
            Fields.DEPTH.value: None,
            Fields.HEIGHT.value: None,
            Fields.LENGTH.value: None,
            Fields.WEIGHT.value: None,
            Fields.METERING.value: None,
            Fields.MOTOR.value: None,
            Fields.HEAT.value: None,
            Fields.CABINET.value: None,
            Fields.ZERO_DISCOUNT_PRICE.value: None,
            Fields.MATERIAL_GROUP_DISCOUNT.value: None,
            Fields.MATERIAL_GROUP_NET_PRICE.value: None,
            Fields.SNP_DISCOUNT.value: None,
            Fields.SNP_PRICE.value: None,
            Fields.NET_PRICE.value: None,
            Fields.RATINGS_AC_TXV.value: None,
            Fields.RATINGS_HP_TXV.value: None,
            Fields.RATINGS_PISTON.value: None,
            Fields.RATINGS_FIELD_TXV.value: None,
        }

    def regex_match(self, pattern: str, ref: str=None) -> bool:
        reference = str(self) if not ref else ref
        try:
            return re.search(pattern, reference) is not None
        except re.error:
            return False