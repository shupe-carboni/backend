import re
from app.adp.adp_models.model_series import ModelSeries, Fields
from app.adp.pricing.s.pricing import load_pricing
from app.db import ADP_DB, Session

class S(ModelSeries):
    text_len = (8,)
    regex = r'''
        (?P<series>S)
        (?P<mat>[M|K|L])
        (?P<scode>\d)
        (?P<meter>\d)
        (?P<ton>\d{2})
        (?P<heat>(\d{2}|(XX)))
    '''
    weight_by_material = {
        'K': 'weight_cu',
        'L': 'weight_cu',
        'M': 'weight_al'
    }
    def __init__(self, re_match: re.Match):
        super().__init__(re_match)
        self.specs = ADP_DB.load_df(session=self.session, table_name='s_dims')
        self.min_qty = 4
        model_specs = self.specs[self.specs['tonnage'] == int(self.attributes['ton'])]
        self.width = model_specs['width'].item()
        self.depth = model_specs['depth'].item()
        self.height = model_specs['height'].item()
        self.weight = model_specs[self.weight_by_material[self.attributes['mat']]].item()
        self.motor = 'PSC Motor' if int(self.attributes['ton']) % 2 == 0 else 'ECM Motor'
        self.metering = self.metering_mapping[int(self.attributes['meter'])]
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps['series'] == self.__series_name__())
            & (self.mat_grps['mat'].str.contains(self.attributes['mat'])),
            'mat_grp'].item()
        self.tonnage = int(self.attributes['ton'])
        self.ratings_ac_txv = fr"""S{self.attributes['mat']}{self.attributes['scode']}\(6,9\){self.tonnage}"""
        self.ratings_hp_txv = fr"""S{self.attributes['mat']}{self.attributes['scode']}9{self.tonnage}"""
        self.ratings_piston = fr"""S{self.attributes['mat']}{self.attributes['scode']}\(1,2\){self.tonnage}"""
        self.ratings_field_txv = fr"""S{self.attributes['mat']}{self.attributes['scode']}\(1,2\){self.tonnage}\+TXV"""
    
    def category(self) -> str:
        motor = self.motor
        return f'Wall Mount Air Handlers - {motor}'

    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = load_pricing(session=self.session)
        pricing_ = pricing_.loc[
            pricing_['model'].apply(lambda regex: self.regex_match(regex)),
            :]
        heat: str = self.attributes['heat']
        result = pricing_[heat].item()
        result += adders_.get(int(self.attributes['meter']),0)
        result += adders_.get(int(self.attributes['ton']),0)
        return result

    def set_heat(self):
        try:
            self.heat = int(self.attributes['heat'])
            self.heat = self.kw_heat[self.heat]
        except Exception as e:
            self.heat = 'Error'
            print(e)

    def record(self) -> dict:
        self.set_heat()
        model_record = super().record()
        values = {
            Fields.MODEL_NUMBER.value: str(self),
            Fields.CATEGORY.value: self.category(),
            Fields.MPG.value: self.mat_grp,
            Fields.SERIES.value: self.__series_name__(),
            Fields.TONNAGE.value: self.tonnage,
            Fields.MIN_QTY.value: self.min_qty,
            Fields.WIDTH.value: self.width,
            Fields.DEPTH.value: self.depth,
            Fields.HEIGHT.value: self.height,
            Fields.WEIGHT.value: self.weight,
            Fields.MOTOR.value: self.motor,
            Fields.METERING.value: self.metering,
            Fields.HEAT.value: self.heat,
            Fields.ZERO_DISCOUNT_PRICE.value: self.calc_zero_disc_price(),
            Fields.RATINGS_AC_TXV.value: self.ratings_ac_txv,
            Fields.RATINGS_HP_TXV.value: self.ratings_hp_txv,
            Fields.RATINGS_PISTON.value: self.ratings_piston,
            Fields.RATINGS_FIELD_TXV.value: self.ratings_field_txv,
        }
        model_record.update(values)
        return model_record