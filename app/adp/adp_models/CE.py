import re
from app.adp.adp_models.model_series import ModelSeries, Fields, Cabinet
from app.adp.utils.validator import Validator
from app.db import ADP_DB, Session

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
    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session,re_match)
        self.specs = ADP_DB.load_df(session=session, table_name='ce_dims')
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
                from app.adp.adp_models.V import V
                self.length = model_specs['length'].item()
                self.height = None
                real_model_obj = V
            case 'M':
                from app.adp.adp_models.MH import MH
                self.length = None
                self.height = model_specs['height'].item()
                real_model_obj = MH
            case 'P':
                from app.adp.adp_models.HE import HE
                self.length = None
                self.height = model_specs['height'].item()
                real_model_obj = HE
            case 'V':
                from app.adp.adp_models.HE import HE
                self.length = None
                self.height = model_specs['height'].item()
                real_model_obj = HE
            case 'S':
                from app.adp.adp_models.HH import HH
                self.length = None
                self.height = model_specs['height'].item()
                real_model_obj = HH

        self.real_model_obj = Validator(session, self.real_model, real_model_obj).is_model()
        self.zero_disc_price = self.real_model_obj.calc_zero_disc_price()
        self.ratings_ac_txv = None
        self.ratings_hp_txv = None
        self.ratings_piston = None
        self.ratings_field_txv = None
                
    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.MODEL_NUMBER.value: self.real_model,
            Fields.PRIVATE_LABEL.value: str(self),
            Fields.CATEGORY.value: self.real_model_obj.category(),
            Fields.SERIES.value: self.real_model_obj.__series_name__(),
            Fields.TONNAGE.value: self.tonnage,
            Fields.MPG.value: self.mat_grp,
            Fields.PALLET_QTY.value: self.pallet_qty,
            Fields.WIDTH.value: self.width,
            Fields.DEPTH.value: self.depth,
            Fields.LENGTH.value: self.length,
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