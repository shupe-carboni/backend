import re
from app.adp.adp_models.model_series import ModelSeries, Fields, Cabinet
import app.adp.pricing.he as pricing
from app.db import ADP_DB, Session

class HE(ModelSeries):
    text_len = (18,)
    regex = r'''
        (?P<paint>[H|A|G|J|N|P|R|T|Y])
        (?P<mat>[E|G])
        (?P<scode>\d{2}|\d\D)
        (?P<meter>\d)
        (?P<ton>\d{2})
        (?P<depth>[A|C|D|E])
        (?P<width>\d{3})
        (?P<notch>B)
        (?P<height>\d{2})
        (?P<config>\d{2})
        (?P<AP>AP)
    '''

    mat_config_map = {
        'E': {
            '01': 'CU_VERT',
            '05': 'CU_VERT',
            '20': 'CU_MP',
            '22': 'CU_MP',
        },
        'G': {
            '01': 'AL_VERT',
            '05': 'AL_VERT',
            '20': 'AL_MP',
            '22': 'AL_MP',
        },
    }
    orientations = {
        '00': ('Right Hand', 'Uncased'),
        '04': ('Left Hand', 'Uncased'),
        '01': ('Right Hand', 'Upflow'),
        '05': ('Left Hand', 'Upflow'),
        '20': ('Right Hand', 'Multiposition'),
        '22': ('Left Hand', 'Multiposition'),
    }

    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        self.pallet_qtys = ADP_DB.load_df(session=session, table_name='he_pallet_qty')
        self.weights = ADP_DB.load_df(session=session, table_name='he_weights')
        if self.attributes['paint'] == 'H':
            self.cabinet_config = Cabinet.EMBOSSED
        else:
            self.cabinet_config = Cabinet.PAINTED
        width: int = int(self.attributes['width'])
        height: int = int(self.attributes['height'])
        if width % 10 == 2:
            self.width = width/10 + 0.05
        else:
            self.width = width/10
        self.depth = self.coil_depth_mapping[self.attributes['depth']]
        self.height = height + 0.5 if self.depth != 'uncased' else height
        self.material = self.material_mapping[self.attributes['mat']]
        self.metering = self.metering_mapping[int(self.attributes['meter'])]
        self.color = self.paint_color_mapping[self.attributes['paint']]
        self.pallet_qty = self.pallet_qtys.loc[self.pallet_qtys['width'] == self.width, str(self.height)].item()
        weight_mask_material = self.weights['SC_0'].str.contains(self.attributes['mat'])
        weight_mask_scode = self.weights['SC_1'] == self.attributes['scode']
        material_orientation_col_mask = self.mat_config_map[self.attributes['mat']][self.attributes['config']]
        self.weight = self.weights.loc[
                (weight_mask_material)
                 & (weight_mask_scode),
                 material_orientation_col_mask].item()
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps['series'] == self.__series_name__())
            & (self.mat_grps['mat'] == self.attributes['mat'])
            & (self.mat_grps['config'].str.contains(self.attributes['config'])),
            'mat_grp'].item()
        self.zero_disc_price = self.calc_zero_disc_price()
        self.tonnage = int(self.attributes['ton'])
        self.ratings_piston = fr"H(,.){1,2}{self.attributes['mat']}{self.attributes['scode']}\(1,2\){self.tonnage}"
        self.ratings_field_txv = fr"H(,.){1,2}{self.attributes['mat']}{self.attributes['scode']}\(1,2\){self.tonnage}\+TXV"
        self.ratings_hp_txv = fr"H(,.){1,2}{self.attributes['mat']}{self.attributes['scode']}9{self.tonnage}"
        self.ratings_ac_txv = fr"H(,.){1,2}{self.attributes['mat']}{self.attributes['scode']}\(6,9\){self.tonnage}"

    def category(self) -> str:
        material = self.material
        color = self.color if self.attributes['paint'] == 'H' else self.color+" Painted"
        connections, orientation = self.orientations[self.attributes['config']]
        additional = 'Cased Coils'
        return f"{orientation} {material} {additional} - {color}"

    
    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = pricing.load_pricing(session=self.session)
        core_configs = ADP_DB.load_df(session=self.session, table_name='he_core_configs')

        if self.depth == 'uncased':
            col = self.depth
        else:
            col = self.cabinet_config.name
            match self.attributes['config']:
                case '01'|'05':
                    col += '_CASED'
                case '20'|'22':
                    col += '_MP'
                case _:
                    return -1
        pricing_ = pricing_.loc[pricing_['slab'] == self.attributes['scode'],col]
        result = pricing_.item()

        # adder for txvs
        result += adders_.get(self.attributes['meter'], 0)

        # adder for non_core depth
        core_depths: str = core_configs.loc[core_configs['series'] == self.attributes['paint'],'depth'].item()
        core_depths_list = [e.strip() for e in core_depths.split(',')]
        depth_core_status = 'core' if self.attributes['depth'] in core_depths_list else 'non-core'
        result += adders_.get(depth_core_status,0)

        # adder for non_core hand
        core_hands: str = core_configs.loc[core_configs['series'] == self.attributes['paint'], 'hand'].item()
        core_hands_list = [e.strip() for e in core_hands.split(',')]
        hand = {
            '01': 'R',
            '05': 'L',
            '20': 'R',
            '22': 'L',
        }
        model_hand = hand[self.attributes['config']]
        hand_core_status = 'core' if model_hand in core_hands_list else 'non-core'
        result += adders_.get(hand_core_status,0)
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