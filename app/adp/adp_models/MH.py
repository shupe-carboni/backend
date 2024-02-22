import re
from app.adp.adp_models.model_series import ModelSeries, Fields, Cabinet
import app.adp.pricing.mh as pricing
from app.db import ADP_DB, Session

class MH(ModelSeries):
    text_len = (7,)
    regex = r'''
        (?P<series>M)
        (?P<ton>\d{2})
        (?P<mat>E)
        (?P<scode>\d{2})
        (?P<meter>\d)
        '''
    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        self.specs = ADP_DB.load_df(session=session, table_name='mh_pallet_weight_height')
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
        pricing_, adders_ = pricing.load_pricing(session=self.session)

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