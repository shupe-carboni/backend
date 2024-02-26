import re
from app.adp.adp_models.model_series import ModelSeries, Fields, Cabinet
import app.adp.pricing.v as pricing
from app.db import ADP_DB, Session

class V(ModelSeries):
    text_len = (11,)
    regex = r'''
        (?P<paint>[V|A|G|J|N|P|R|T|Y|C])
        (?P<ton>\d{2})
        (?P<type>H)
        (?P<height>\d{3})
        (?P<mat>[D|P])
        (?P<scode>\d{2})
        (?P<meter>\d)
        '''
    material_weight = {
        'D': 'WEIGHT_CU',
        'P': 'WEIGHT_AL'
    }
    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        self.specs = ADP_DB.load_df(session=session, table_name='v_or_hd_len_pallet_weights')
        if self.attributes['paint'] == 'V':
            self.cabinet_config = Cabinet.EMBOSSED
        else:
            self.cabinet_config = Cabinet.PAINTED
        height = int(self.attributes['height'])
        if height % 10 == 2:
            self.height = height/10 + 0.05
        else:
            self.height = height/10
        if self.height < 17:
            height_str = r'\*\*\*'
        else:
            height_str = self.attributes['height']
        self.material = self.material_mapping[self.attributes['mat']]
        self.metering = self.metering_mapping[int(self.attributes['meter'])]
        self.color = self.paint_color_mapping[self.attributes['paint']]
        self.width = 21
        model_specs = self.specs.loc[self.specs['SC_1'] == int(self.attributes['scode'])]
        self.pallet_qty = model_specs['pallet_qty'].item()
        self.length = model_specs['length'].item()
        self.weight = model_specs[self.material_weight[self.attributes['mat']]].item()
        self.zero_disc_price = self.calc_zero_disc_price()
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps['series'] == self.__series_name__())
            & (self.mat_grps['mat'] == self.attributes['mat']),
            'mat_grp'].item()
        self.tonnage = int(self.attributes['ton'])
        if self.cabinet_config != Cabinet.PAINTED:
            self.ratings_ac_txv = fr'V,.{self.tonnage}H{height_str}{self.attributes['mat']}{self.attributes['scode']}\(6,9\)'
            self.ratings_hp_txv = fr'V,.{self.tonnage}H{height_str}{self.attributes['mat']}{self.attributes['scode']}9'
            self.ratings_piston = fr'V,.{self.tonnage}H{height_str}{self.attributes['mat']}{self.attributes['scode']}\(1,2\)'
            self.ratings_field_txv = fr'V,.{self.tonnage}H{height_str}{self.attributes['mat']}{self.attributes['scode']}\(1,2\)\+TXV'
        else:
            self.ratings_ac_txv = fr'V(,.){{0,2}},{self.attributes['paint']}(,.){{0,1}}{self.tonnage}H{height_str}{self.attributes['mat']}{self.attributes['scode']}\(6,9\)'
            self.ratings_hp_txv = fr'V(,.){{0,2}},{self.attributes['paint']}(,.){{0,1}}{self.tonnage}H{height_str}{self.attributes['mat']}{self.attributes['scode']}9'
            self.ratings_piston = fr'V(,.){{0,2}},{self.attributes['paint']}(,.){{0,1}}{self.tonnage}H{height_str}{self.attributes['mat']}{self.attributes['scode']}\(1,2\)'
            self.ratings_field_txv = fr'V(,.){{0,2}},{self.attributes['paint']}(,.){{0,1}}{self.tonnage}H{height_str}{self.attributes['mat']}{self.attributes['scode']}\(1,2\)\+TXV'

    def category(self) -> str:
        material = self.material
        paint = self.color
        return f'Dedicated Horizontal "A" {material} Coils - {paint}'
    
    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = pricing.load_pricing(session=self.session)
        result = pricing_.loc[
            pricing_['slab'] == int(self.attributes['scode']),
            self.cabinet_config.name
            ].item()
        result += adders_.get(int(self.attributes['meter']),0)
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