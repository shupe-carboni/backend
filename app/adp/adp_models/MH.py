import re
from adp_models.model_series import ModelSeries, Fields, Cabinet
import pricing
from db.db import Database

DATABASE = Database('adp')


class MH(ModelSeries):
    text_len = (7,)
    regex = r'''
        (?P<series>M)
        (?P<ton>\d{2})
        (?P<mat>E)
        (?P<scode>\d{2})
        (?P<meter>\d)
        '''
    specs = DATABASE.load_df('mh_pallet_weight_height')
    def __init__(self, re_match: re.Match):
        super().__init__(re_match)
        self.cabinet_config = Cabinet.UNCASED
        self.metering = self.metering_mapping[int(self.attributes['meter'])]
        self.material = 'Copper'
        self.width = 18
        self.depth = 19.5
        model_specs = self.specs[self.specs['SC_1'] == int(self.attributes['scode'])]
        self.height = model_specs['HEIGHT'].item()
        self.pallet_qty = model_specs['PALLET_QTY'].item()
        self.weight = model_specs['WEIGHT'].item()
        self.zero_disc_price = self.calc_zero_disc_price()
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps['series'] == self.__series_name__()),
            'mat_grp'].item()
        self.tonnage = int(self.attributes['ton'])
        self.ratings_ac_txv = fr'M{self.tonnage}{self.attributes['mat']}{self.attributes['scode']}\(6,9\)'
        self.ratings_hp_txv = fr'M{self.tonnage}{self.attributes['mat']}{self.attributes['scode']}9'
        self.ratings_piston = fr'M{self.tonnage}{self.attributes['mat']}{self.attributes['scode']}\(1,2\)'
        self.ratings_field_txv = fr'M{self.tonnage}{self.attributes['mat']}{self.attributes['scode']}\(1,2\)\+TXV'

    def category(self) -> str:
        return "Manufactured Housing Coils"

    def calc_zero_disc_price(self) -> int:
        pricing_ = pricing.mh.pricing
        adders_ = pricing.mh.adders

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