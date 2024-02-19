import re
from adp_models.model_series import ModelSeries, Fields, Cabinet
from utils.validator import Validator
from app.db import Database

DATABASE = Database('adp')

class CE(ModelSeries):
    text_len = (10,)
    regex = r'''
        (?P<series>CE)
        (?P<config>[H|M|P|S|V])
        (?P<ton>\d{2})
        (?P<width_height>\d{2})
        (?P<mat>[E|G|H|D|P])
        (?P<scode>\d{2})
    '''
    ce_configurations = {
        'H': ('Horizontal','CR'),
        'M': ('Mobile Home','CO'),
        'P': ('Multi-position','CM'),
        'S': ('Slab','CD'),
        'V': ('Vertical', 'CA')
    }
    specs = DATABASE.load_df('ce_dims')
    def __init__(self, re_match: re.Match):
        super().__init__(re_match)
        self.configuration = self.ce_configurations[self.attributes['config']]
        self.mat_grp = self.configuration[1]
        self.cabinet_config = Cabinet.PAINTED
        self.metering = self.metering_mapping[9]
        model_specs = self.specs[self.specs['model'] == str(self)]
        self.pallet_qty = model_specs['pallet_qty'].item()
        self.width = model_specs['width'].item()
        self.depth = model_specs['depth'].item()
        self.weight = model_specs['weight'].item()
        self.real_model = model_specs['adp_model'].item()
        self.tonnage = int(self.attributes['ton'])
        match self.attributes['config']:
            case 'H':
                from adp_models.V import V
                self.length = model_specs['length'].item()
                self.height = None
                real_model_obj = V
            case 'M':
                from adp_models.MH import MH
                self.length = None
                self.height = model_specs['height'].item()
                real_model_obj = MH
            case 'P':
                from adp_models.HE import HE
                self.length = None
                self.height = model_specs['height'].item()
                real_model_obj = HE
            case 'V':
                from adp_models.HE import HE
                self.length = None
                self.height = model_specs['height'].item()
                real_model_obj = HE
            case 'S':
                from adp_models.HH import HH
                self.length = None
                self.height = model_specs['height'].item()
                real_model_obj = HH

        self.real_model_obj = Validator(self.real_model, real_model_obj).is_model()
        self.zero_disc_price = self.real_model_obj.calc_zero_disc_price()
        self.ratings_ac_txv = None
        self.ratings_hp_txv = None
        self.ratings_piston = None
        self.ratings_field_txv = None
                
    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.MODEL_NUMBER.formatted(): self.real_model,
            Fields.PRIVATE_LABEL.formatted(): str(self),
            Fields.CATEGORY.formatted(): self.real_model_obj.category(),
            Fields.SERIES.formatted(): self.real_model_obj.__series_name__(),
            Fields.TONNAGE.formatted(): self.tonnage,
            Fields.MPG.name: self.mat_grp,
            Fields.PALLET_QTY.formatted(): self.pallet_qty,
            Fields.WIDTH.formatted(): self.width,
            Fields.DEPTH.formatted(): self.depth,
            Fields.LENGTH.formatted(): self.length,
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