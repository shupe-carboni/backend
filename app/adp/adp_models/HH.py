import re
from app.adp.adp_models.model_series import ModelSeries, Fields, Cabinet
import app.adp.pricing.hh as pricing
from app.db import ADP_DB

session = next(ADP_DB.get_db())


class HH(ModelSeries):
    text_len = (18,)
    regex = r'''
        (?P<paint>H)
        (?P<mat>H)
        (?P<scode>\d{2})
        (?P<meter>\d)
        (?P<ton>\d{2})
        (?P<depth>A)
        (?P<width>\d{3})
        (?P<notch>A)
        (?P<height>\d{2})
        (?P<config>\d{2})
        (?P<AP>AP)
    '''

    def __init__(self, re_match: re.Match):
        super().__init__(re_match)
        self.specs = ADP_DB.load_df(session=session, table_name='hh_weights_pallet')
        self.cabinet_config = Cabinet.EMBOSSED
        width = int(self.attributes['width'])
        self.width = width//10 + (5/8) + 4 + (3/8)
        self.depth = 10
        self.height = int(self.attributes['height']) + 0.25 + 1.5
        self.metering = self.metering_mapping[int(self.attributes['meter'])]
        self.material = 'Copper'
        model_specs = self.specs.loc[self.specs['SC_1'] == int(self.attributes['scode'])]
        self.pallet_qty = model_specs['pallet_qty'].item()
        self.weight = model_specs['WEIGHT'].item()
        self.zero_disc_price = self.calc_zero_disc_price()
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps['series'] == self.__series_name__()),
            'mat_grp'].item()
        self.tonnage = int(self.attributes['ton'])
        self.ratings_ac_txv = fr"""HH{self.attributes['scode']}\(6,9\){self.tonnage}"""
        self.ratings_hp_txv = fr"""HH{self.attributes['scode']}9{self.tonnage}"""
        self.ratings_piston = fr"""HH{self.attributes['scode']}\(1,2\){self.tonnage}"""
        self.ratings_field_txv = fr"""HH{self.attributes['scode']}\(1,2\){self.tonnage}\+TXV"""

    def category(self) -> str:
        return "Horizontal Slab Coils"
    
    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = pricing.load_pricing(session=session)

        result = pricing_.loc[pricing_['slab'] == int(self.attributes['scode']),'price'].item()
        result += adders_.get(int(self.attributes['meter']), 0)
        return result


    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.MODEL_NUMBER.value: str(self),
            Fields.CATEGORY.value: self.category(),
            Fields.MPG.value: self.mat_grp,
            Fields.SERIES.value: self.__series_name__(),
            Fields.TONNAGE.value: self.tonnage,
            Fields.PALLET_QTY.value: self.pallet_qty,
            Fields.WIDTH.value: self.width,
            Fields.DEPTH.value: self.depth,
            Fields.HEIGHT.value: self.height,
            Fields.WEIGHT.value: self.weight,
            Fields.CABINET.value: self.cabinet_config.name.title(),
            Fields.METERING.value: self.metering,
            Fields.ZERO_DISCOUNT_PRICE.value: self.zero_disc_price,
            Fields.RATINGS_AC_TXV.value: self.ratings_ac_txv,
            Fields.RATINGS_HP_TXV.value: self.ratings_hp_txv,
            Fields.RATINGS_PISTON.value: self.ratings_piston,
            Fields.RATINGS_FIELD_TXV.value: self.ratings_field_txv,
        }
        model_record.update(values)
        return model_record