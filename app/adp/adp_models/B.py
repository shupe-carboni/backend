import re
import pricing
from adp_models.model_series import ModelSeries, Fields
from db.db import Database

DATABASE = Database('adp')

class B(ModelSeries):
    text_len = (13,)
    regex = r'''
        (?P<series>B)
        (?P<motor>[C|V])
        (?P<hpanpos>[R|O])
        (?P<config>M)
        (?P<scode>\D\d|(00))
        (?P<meter>\d)
        (?P<ton>\d{2})
        (?P<line_conn>S)
        (?P<heat>\d[0|P|N])
        (?P<voltage>\d)
        '''
    specs = DATABASE.load_df('b_dims')
    hydronic_heat = {
        '00': 'no heat',
        '2P': '2 row hot water coil with pump assembly',
        '3P': '3 row hot water coil with pump assembly',
        '4P': '4 row hot water coil with pump assembly',
        '2N': '2 row hot water coil without pump assembly',
        '3N': '3 row hot water coil without pump assembly',
        '4N': '4 row hot water coil without pump assembly',
    }
    def __init__(self, re_match: re.Match):
        super().__init__(re_match)
        self.min_qty = 4
        model_specs = self.specs[self.specs['tonnage'] == int(self.attributes['ton'])]
        self.width = model_specs['width'].item()
        self.depth = model_specs['depth'].item()
        self.height = model_specs['height'].item()
        self.weight = model_specs['weight'].item()
        self.motor = self.motors[self.attributes['motor']]
        self.metering = self.metering_mapping[int(self.attributes['meter'])]
        self.heat = self.hydronic_heat[self.attributes['heat']]
        self.zero_disc_price = self.calc_zero_disc_price()
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps['series'] == self.__series_name__()),
            'mat_grp'].item()
        self.tonnage = int(self.attributes['ton'])
        self.ratings_ac_txv = fr'B{self.attributes['motor']}\*\*{self.attributes['scode']}\(6,9\){self.tonnage}'
        self.ratings_hp_txv = fr'B{self.attributes['motor']}\*\*{self.attributes['scode']}9{self.tonnage}'
        self.ratings_piston = fr'B{self.attributes['motor']}\*\*{self.attributes['scode']}\(1,2\){self.tonnage}'
        self.ratings_field_txv = fr'B{self.attributes['motor']}\*\*{self.attributes['scode']}\(1,2\){self.tonnage}\+TXV'

    def category(self) -> str:
        orientation = 'Multiposition'
        motor = self.motor
        return f'Hydronic {orientation} Air Handlers - {motor}'
    
    def calc_zero_disc_price(self) -> int:
        adders_ = pricing.b.adders
        pricing_ = pricing.b.pricing
        pricing_ = pricing_.loc[
            (pricing_['tonnage'] == int(self.attributes['ton']))
            & (pricing_['slab'] == self.attributes['scode']), :]
        if pricing_.empty:
            return -1
        heat: str = self.attributes['heat']
        result = pricing_[heat[0]].item() if heat != '00' else pricing_['base'].item()
        result += adders_.get(int(self.attributes['meter']),0)
        result += adders_.get(int(self.attributes['voltage']),0)
        result += adders_.get(self.attributes['heat'][-1],0)
        result += adders_.get(self.attributes['motor'],0)
        return result

    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.MODEL_NUMBER.formatted(): str(self),
            Fields.CATEGORY.formatted(): self.category(),
            Fields.MPG.name: self.mat_grp,
            Fields.SERIES.formatted(): self.__series_name__(),
            Fields.TONNAGE.formatted(): self.tonnage,
            Fields.MIN_QTY.formatted(): self.min_qty,
            Fields.WIDTH.formatted(): self.width,
            Fields.DEPTH.formatted(): self.depth,
            Fields.HEIGHT.formatted(): self.height,
            Fields.WEIGHT.formatted(): self.weight,
            Fields.MOTOR.formatted(): self.motor,
            Fields.METERING.formatted(): self.metering,
            Fields.HEAT.formatted(): self.heat,
            Fields.ZERO_DISCOUNT_PRICE.formatted(): self.zero_disc_price,
            Fields.RATINGS_AC_TXV.formatted(): self.ratings_ac_txv,
            Fields.RATINGS_HP_TXV.formatted(): self.ratings_hp_txv,
            Fields.RATINGS_PISTON.formatted(): self.ratings_piston,
            Fields.RATINGS_FIELD_TXV.formatted(): self.ratings_field_txv,
        }
        model_record.update(values)
        return model_record