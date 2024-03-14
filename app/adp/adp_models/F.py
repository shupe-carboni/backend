import re
from app.adp.adp_models.model_series import ModelSeries, Fields
from app.adp.pricing.f.pricing import load_pricing
from app.db import ADP_DB, Session

class F(ModelSeries):
    text_len = (13,)
    regex = r'''
        (?P<series>F)
        (?P<motor>[C|E])
        (?P<config>M)
        (?P<scode>\D{2}\d|\D\d{2})
        (?P<meter>\d)
        (?P<ton>\d{2})
        (?P<line_conn>[S|B])
        (?P<heat>\d{2})
        (?P<voltage>\d)
        '''
    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        self.specs = ADP_DB.load_df(session=session, table_name='f_dims')
        self.min_qty = 4
        model_specs = self.specs[self.specs['tonnage'] == int(self.attributes['ton'])]
        self.width = model_specs['width'].item()
        self.depth = model_specs['depth'].item()
        self.height = model_specs['height'].item()
        self.weight = model_specs['weight'].item()
        self.motor = self.motors[self.attributes['motor']]
        self.metering = self.metering_mapping[int(self.attributes['meter'])]
        self.heat = self.kw_heat[int(self.attributes['heat'])]
        self.zero_disc_price = self.calc_zero_disc_price()
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps['series'] == self.__series_name__())
            & (self.mat_grps['mat'].str.contains(re.sub(r'\d+','',self.attributes['scode']))),
            'mat_grp'].item()
        self.tonnage = int(self.attributes['ton'])
        s_code = self.attributes['scode']
        self.s_code_mat = s_code[0] if s_code[0] in ('E','G') else s_code[:2]
        self.ratings_ac_txv = fr"""F,P{self.attributes['motor']}\*{s_code}\(6,9\){self.tonnage}"""
        self.ratings_hp_txv = fr"""F,P{self.attributes['motor']}\*{s_code}9{self.tonnage}"""
        self.ratings_piston = fr"""F,P{self.attributes['motor']}\*{s_code}\(1,2\){self.tonnage}"""
        self.ratings_field_txv = fr"""F,P{self.attributes['motor']}\*{s_code}\(1,2\){self.tonnage}\+TXV"""


    def category(self) -> str:
        orientation = 'Multiposition'
        motor = self.motor
        return f'Low Profile {orientation} Air Handlers - {motor}'

    def calc_zero_disc_price(self) -> int:
        pricing_, adders_= load_pricing(session=self.session)
        pricing_ = pricing_.loc[
            (pricing_['slab'].apply(lambda regex: self.regex_match(regex, self.attributes['scode'])))
            & (pricing_['tonnage'] == int(self.attributes['ton'])),:]
        heat: str = self.attributes['heat']
        if heat != '00':
            result = pricing_[heat].item()
        else:
            result = pricing_['base'].item()
        result += adders_.get(self.attributes['voltage'],0)
        result += adders_.get(self.attributes['line_conn'],0) if heat == '05' else 0
        result += adders_.get(self.attributes['ton'],0) if self.attributes['motor'] == 'E' else 0
        result += adders_.get(self.attributes['meter'],0)        
        return result

    def record(self) -> dict:
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
            Fields.ZERO_DISCOUNT_PRICE.value: self.zero_disc_price,
            Fields.RATINGS_AC_TXV.value: self.ratings_ac_txv,
            Fields.RATINGS_HP_TXV.value: self.ratings_hp_txv,
            Fields.RATINGS_PISTON.value: self.ratings_piston,
            Fields.RATINGS_FIELD_TXV.value: self.ratings_field_txv,
        }
        model_record.update(values)
        return model_record