import re
from adp_models.model_series import ModelSeries, Fields
import pricing
from app.db import Database

DATABASE = Database('adp')

class CP(ModelSeries):
    text_len = (14,13)
    regex = r'''
        (?P<series>C)
        (?P<motor>[P|E])
        (?P<ton>\d{2})
        (?P<scode>\d{2})
        (?P<mat>\D)
        (?P<meter>[A|H])
        (?P<config>H)
        (?P<line_conn>[S|P])
        (?P<heat>\d{2})
        (?P<voltage>\d)
        (?P<option>C?)
        (?P<drain>R?)
    '''
    specs = DATABASE.load_df('cp_dims')
    metering_mapping_ = {
        'A': 'Piston (R-410A) w/ Access Port',
        'H': 'Non-bleed HP-A/C TXV (R-410A)'
    }
    def __init__(self, re_match: re.Match):
        super().__init__(re_match)
        self.pallet_qty = 8
        model_specs = self.specs.loc[
                (self.specs['series'] == self.attributes['series'])
                & (self.specs['motor'] == self.attributes['motor'])
                & (self.specs['ton'] == int(self.attributes['ton']))
                & (self.specs['cased'] == (self.attributes.get('option') == "C")),:]
        self.width = model_specs['width'].item()
        self.depth = model_specs['depth'].item()
        self.height = model_specs['height'].item()
        self.weight = model_specs['weight'].item()
        self.cased = self.attributes.get('option') == "C"
        self.motor = self.motors[self.attributes['motor']]
        self.metering = self.metering_mapping_[self.attributes['meter']]
        self.zero_disc_price = self.get_zero_disc_price()
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps['series'] == self.__series_name__()),
            'mat_grp'].item()
        self.tonnage = int(self.attributes['ton'])
        self.ratings_ac_txv = fr"C{self.attributes['motor']}{self.tonnage}{self.attributes['scode']}{self.attributes['mat']}\+TXV"
        self.ratings_hp_txv = self.ratings_ac_txv
        self.ratings_piston = fr"C{self.attributes['motor']}{self.tonnage}{self.attributes['scode']}{self.attributes['mat']}"
        self.ratings_field_txv = self.ratings_ac_txv
    
        try:
            self.heat = int(self.attributes['heat'])
            self.heat = self.kw_heat[self.heat]
        except Exception as e:
            self.heat = "error"

    def category(self) -> str:
        material = self.material_mapping[self.attributes['mat']]
        motor = self.motor
        cased = 'Uncased' if not self.cased else 'Cased'
        return f'Soffit Mount {cased} Air Handlers - {material} - {motor}'

    def get_zero_disc_price(self) -> int:
        pricing_ = pricing.cp.pricing
        return pricing_.loc[pricing_[self.attributes['mat']] == str(self),'price'].item()

    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.MODEL_NUMBER.formatted(): str(self),
            Fields.CATEGORY.formatted(): self.category(),
            Fields.SERIES.formatted(): self.__series_name__(),
            Fields.MPG.name: self.mat_grp,
            Fields.TONNAGE.formatted(): self.tonnage,
            Fields.PALLET_QTY.formatted(): self.pallet_qty,
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