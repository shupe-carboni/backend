import re
from app.adp.adp_models.model_series import ModelSeries, Fields, Cabinet
import app.adp.pricing.sc as pricing
from app.db import Database

DATABASE = Database('adp')

class SC(ModelSeries):
    text_len = (7,)
    regex = r'''
        (?P<series>S)
        (?P<ton>\d{2})
        (?P<mat>[R|L|H|S])
        (?P<width_height>\d{3})
        '''
    configs = {
        'R': ('Right Hand Upflow','Copper'),
        'L': ('Left Hand Upflow','Copper'),
        'H': ('Horizontal','Aluminum'),
        'S': ('Horizontal Slab','Copper')
    }
    specs = DATABASE.load_df('sc_all_features')
    def __init__(self, re_match: re.Match):
        super().__init__(re_match)
        self.metering = 'Piston (R-410a or R-22)'
        width_height: int = int(self.attributes['width_height'])
        if width_height % 10 in (2,7):
            self.width_height = width_height / 10 + 0.05
        else:
            self.width_height = width_height / 10
        config = self.configs[self.attributes['mat']]
        self.config = config[0]
        self.material = config[1]
        model_specs = self.specs[self.specs['regex'].apply(lambda regex: self.regex_match(regex))]
        if self.attributes['mat'] == 'S':
            model_specs = model_specs.loc[model_specs['height']*10 // 1 == width_height]
        self.pallet_qty = model_specs['pallet_qty'].item()
        self.depth = model_specs['depth'].item()
        self.width = model_specs['width'].item()
        self.height = model_specs['height'].item()
        self.cased = model_specs['cased'].item()
        self.cabinet_config: Cabinet = Cabinet.EMBOSSED if self.cased else Cabinet.UNCASED
        self.weight = model_specs['weight'].item()
        self.zero_disc_price = self.calc_zero_disc_price()
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps['series'] == self.__series_name__())
            & (self.mat_grps['mat'].str.contains(self.attributes['mat']))
            # self.cased is bool - the config column has bool only sometimes
            # so pandas keeps bools as literal strings of 'TRUE' and 'FALSE'
            & (self.mat_grps['config'] == str(self.cased).upper()),
            'mat_grp'].item()
        self.tonnage = int(self.attributes['ton'])
        self.ratings_ac_txv = None
        self.ratings_hp_txv = None
        self.ratings_piston = None
        self.ratings_field_txv = None

    def category(self) -> str:
        seer = '10 SEER'
        cased = 'Uncased' if not self.cased else 'Cased'
        config = self.config
        return f'{seer} {config} Service Coils - {cased}'

    def calc_zero_disc_price(self) -> int:
        pricing_ = pricing.pricing
        pricing_ = pricing_.loc[
            pricing_['model'].apply(lambda regex: self.regex_match(regex)),
            :]
        match self.attributes['mat']:
            case 'R'|'L':
                result = pricing_[str(int(self.cased))].item()
            case 'S':
                result = pricing_[str(int(self.height > 19))].item()
            case 'H':
                result = pricing_[str(1)].item()
            case _:
                result = -1
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
            Fields.HEIGHT.formatted(): self.height,
            Fields.DEPTH.formatted(): self.depth,
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