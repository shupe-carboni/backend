import re
from adp_models.model_series import ModelSeries, Fields, Cabinet
import pricing
from app.db import Database

DATABASE = Database('adp')


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
    specs = DATABASE.load_df('hh_weights_pallet')

    def __init__(self, re_match: re.Match):
        super().__init__(re_match)
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
        self.ratings_ac_txv = fr'HH{self.attributes['scode']}\(6,9\){self.tonnage}'
        self.ratings_hp_txv = fr'HH{self.attributes['scode']}9{self.tonnage}'
        self.ratings_piston = fr'HH{self.attributes['scode']}\(1,2\){self.tonnage}'
        self.ratings_field_txv = fr'HH{self.attributes['scode']}\(1,2\){self.tonnage}\+TXV'

    def category(self) -> str:
        return "Horizontal Slab Coils"
    
    def calc_zero_disc_price(self) -> int:
        pricing_ = pricing.hh.pricing
        adders_ = pricing.hh.adders

        result = pricing_.loc[pricing_['slab'] == int(self.attributes['scode']),'price'].item()
        result += adders_.get(int(self.attributes['meter']), 0)
        return result


    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.MODEL_NUMBER.formatted(): str(self),
            Fields.CATEGORY.formatted(): self.category(),
            Fields.MPG.name: self.mat_grp,
            Fields.SERIES.formatted(): self.__series_name__(),
            Fields.TONNAGE.formatted(): self.tonnage,
            Fields.PALLET_QTY.formatted(): self.pallet_qty,
            Fields.WIDTH.formatted(): self.width,
            Fields.DEPTH.formatted(): self.depth,
            Fields.HEIGHT.formatted(): self.height,
            Fields.WEIGHT.formatted(): self.weight,
            Fields.CABINET.formatted(): self.cabinet_config.name.title(),
            Fields.METERING.formatted(): self.metering,
            Fields.ZERO_DISCOUNT_PRICE.formatted(): self.zero_disc_price,
            Fields.RATINGS_AC_TXV.formatted(): self.ratings_ac_txv,
            Fields.RATINGS_HP_TXV.formatted(): self.ratings_hp_txv,
            Fields.RATINGS_PISTON.formatted(): self.ratings_piston,
            Fields.RATINGS_FIELD_TXV.formatted(): self.ratings_field_txv,
        }
        model_record.update(values)
        return model_record