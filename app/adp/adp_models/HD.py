import re
from adp_models.model_series import ModelSeries, Fields, Cabinet
from db.db import Database

DATABASE = Database('adp')

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
    specs = DATABASE.load_df('v_or_hd_len_pallet_weights')

    def __init__(self, re_match: re.Match):
        super().__init__(re_match)
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
        self.weight = model_specs['weight'].item()
        self.zero_disc_price = None
        self.tonnage = int(self.attributes['ton'])
        self.ratings_ac_txv = None
        self.ratings_hp_txv = None
        self.ratings_piston = None
        self.ratings_field_txv = None

    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.MODEL_NUMBER.formatted(): str(self),
            Fields.SERIES.formatted(): self.__series_name__(),
            Fields.TONNAGE.formatted(): self.tonnage,
            Fields.PALLET_QTY.formatted(): self.pallet_qty,
            Fields.WIDTH.formatted(): self.width,
            Fields.DEPTH.formatted(): self.depth,
            Fields.HEIGHT.formatted(): self.height,
            Fields.WEIGHT.formatted(): self.weight,
            Fields.CABINET.formatted(): self.cabinet_config.name.title(),
            Fields.METERING.formatted(): self.metering,
            Fields.NET_PRICE.formatted(): self.zero_disc_price,
            Fields.RATINGS_AC_TXV.formatted(): self.ratings_ac_txv,
            Fields.RATINGS_HP_TXV.formatted(): self.ratings_hp_txv,
            Fields.RATINGS_PISTON.formatted(): self.ratings_piston,
            Fields.RATINGS_FIELD_TXV.formatted(): self.ratings_field_txv,
        }
        model_record.update(values)
        return model_record