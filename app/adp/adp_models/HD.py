import re
from app.adp.adp_models.model_series import ModelSeries, Fields, Cabinet
from app.adp.pricing.hd.pricing import load_pricing
from app.db import ADP_DB, Session

class HD(ModelSeries):
    text_len = (18,)
    regex = r'''
        (?P<paint>[H|A|G|J|N|P|R|T|Y])
        (?P<mat>[D|P])
        (?P<scode>\d{2})
        (?P<meter>\d)
        (?P<ton>\d{2})
        (?P<depth>E)
        (?P<width>\d{3})
        (?P<notch>B)
        (?P<height>\d{2})
        (?P<config>\d{2})
        (?P<AP>AP)
    '''
    material_weight = {
        'D': 'WEIGHT_CU',
        'P': 'WEIGHT_AL'
    }
    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        self.specs = ADP_DB.load_df(session=session, table_name='v_or_hd_len_pallet_weights')
        if self.attributes['paint'] == 'H':
            self.cabinet_config = Cabinet.EMBOSSED
        else:
            self.cabinet_config = Cabinet.PAINTED
        width: int = int(self.attributes['width'])
        if width % 10 == 2:
            self.width = width/10 + 0.05
        else:
            self.width = width/10
        self.depth = self.coil_depth_mapping[self.attributes['depth']]
        self.height = int(self.attributes['height']) + 0.5
        self.material = self.material_mapping[self.attributes['mat']]
        self.metering = self.metering_mapping[int(self.attributes['meter'])]
        self.color = self.paint_color_mapping[self.attributes['paint']]
        model_specs = self.specs.loc[self.specs['SC_1'] == int(self.attributes['scode'])]
        self.pallet_qty = model_specs['pallet_qty'].item()
        # self.weight = model_specs['weight'].item()
        self.weight = model_specs[self.material_weight[self.attributes['mat']]].item()
        self.zero_disc_price = self.calc_zero_disc_price()
        self.tonnage = int(self.attributes['ton'])
        if self.cabinet_config != Cabinet.PAINTED:
            self.ratings_piston = fr"H(,.){{1,2}}{self.attributes['mat']}{self.attributes['scode']}\(1,2\){self.tonnage}"
            self.ratings_field_txv = fr"H(,.){{1,2}}{self.attributes['mat']}{self.attributes['scode']}\(1,2\){self.tonnage}\+TXV"
            self.ratings_hp_txv = fr"H(,.){{1,2}}{self.attributes['mat']}{self.attributes['scode']}9{self.tonnage}"
            self.ratings_ac_txv = fr"H(,.){{1,2}}{self.attributes['mat']}{self.attributes['scode']}\(6,9\){self.tonnage}"
        else:
            self.ratings_piston = fr"H(,.){{0,2}},{self.attributes['paint']}(,.){{0,1}}{self.attributes['mat']}{self.attributes['scode']}\(1,2\){self.tonnage}"
            self.ratings_field_txv = fr"H(,.){{0,2}},{self.attributes['paint']}(,.){{0,1}}{self.attributes['mat']}{self.attributes['scode']}\(1,2\){self.tonnage}\+TXV"
            self.ratings_hp_txv = fr"H(,.){{0,2}},{self.attributes['paint']}(,.){{0,1}}{self.attributes['mat']}{self.attributes['scode']}9{self.tonnage}"
            self.ratings_ac_txv = fr"H(,.){{0,2}},{self.attributes['paint']}(,.){{0,1}}{self.attributes['mat']}{self.attributes['scode']}\(6,9\){self.tonnage}"
    
    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = load_pricing(session=self.session)
        col = self.cabinet_config.value
        pricing = pricing_.loc[pricing_['slab'] == self.attributes['scode'], col]
        result = pricing.item()
        result += adders_.get(self.attributes['meter'],0)
        return result

    def category(self) -> str:
        material = self.material
        color = self.color
        additional = 'Dedicated Horizontal Coils - Side Connections'
        return f"{material} {additional} - {color}"

    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.MODEL_NUMBER.value: str(self),
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