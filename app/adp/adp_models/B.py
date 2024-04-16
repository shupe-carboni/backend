import re
from numpy import isnan
from app.adp.pricing.b.pricing import load_pricing
from app.adp.adp_models.model_series import ModelSeries, Fields
from app.db import ADP_DB, Session

class B(ModelSeries):
    text_len = (13,14)
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
        (?P<rds>[N|R]?)
        '''
    class InvalidHeatOption(Exception): ...
    hydronic_heat = {
        '00': 'no heat',
        '2P': '2 row hot water coil with pump assembly',
        '3P': '3 row hot water coil with pump assembly',
        '4P': '4 row hot water coil with pump assembly',
        '2N': '2 row hot water coil without pump assembly',
        '3N': '3 row hot water coil without pump assembly',
        '4N': '4 row hot water coil without pump assembly',
    }
    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        self.min_qty = 4
        dims_sql = """
            SELECT weight, height, depth, width
            FROM b_dims
            WHERE tonnage = :tonnage;
        """
        specs = ADP_DB.execute(
            session=session,
            sql=dims_sql,
            params={'tonnage': int(self.attributes['ton'])}
            ).mappings().one_or_none()
        self.width = specs['width']
        self.depth = specs['depth']
        self.height = specs['height']
        self.weight = specs['weight']
        self.motor = self.motors[self.attributes['motor']]
        self.metering = self.metering_mapping[int(self.attributes['meter'])]
        self.heat = self.hydronic_heat[self.attributes['heat']]
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps['series'] == self.__series_name__()),
            'mat_grp'].item()
        self.tonnage = int(self.attributes['ton'])
        self.ratings_ac_txv = fr"B{self.attributes['motor']}"\
            fr"\*\*{self.attributes['scode']}"\
            fr"\(6,9\){self.tonnage}"
        self.ratings_hp_txv = fr"B{self.attributes['motor']}"\
            fr"\*\*{self.attributes['scode']}"\
            fr"9{self.tonnage}"
        self.ratings_piston = fr"B{self.attributes['motor']}"\
            fr"\*\*{self.attributes['scode']}"\
            fr"\(1,2\){self.tonnage}"
        self.ratings_field_txv = fr"B{self.attributes['motor']}"\
            fr"\*\*{self.attributes['scode']}"\
            fr"\(1,2\){self.tonnage}\+TXV"
        self.is_flex_coil = True if self.attributes.get('rds') else False
        self.zero_disc_price = self.calc_zero_disc_price()

    def category(self) -> str:
        orientation = 'Multiposition'
        motor = self.motor
        value = f'Hydronic {orientation} Air Handlers - {motor}'
        if self.is_flex_coil:
            value += ' - FlexCoil'
        return value
    
    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = load_pricing(
            session=self.session,
            series=self.__series_name__(),
            tonnage=str(self.tonnage),
            slab=self.attributes['scode'],
        )
        heat: str = self.attributes['heat']
        if not pricing_:
            raise self.NoBasePrice
        result =  pricing_['base']
        try:
            heat_option = pricing_[heat[0]] if heat != '00' else 0
        except:
            raise self.InvalidHeatOption
        result += heat_option
        result += adders_.get(self.attributes['meter'],0)
        result += adders_.get(self.attributes['voltage'],0)
        result += adders_.get(self.attributes['heat'][-1],0)
        result += adders_.get(self.attributes['motor'],0)
        if self.is_flex_coil:
            result += 10
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