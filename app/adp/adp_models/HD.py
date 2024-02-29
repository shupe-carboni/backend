import re
from app.adp.adp_models.model_series import ModelSeries, Fields, Cabinet
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
            Fields.NET_PRICE.value: self.zero_disc_price,
            Fields.RATINGS_AC_TXV.value: self.ratings_ac_txv,
            Fields.RATINGS_HP_TXV.value: self.ratings_hp_txv,
            Fields.RATINGS_PISTON.value: self.ratings_piston,
            Fields.RATINGS_FIELD_TXV.value: self.ratings_field_txv,
        }
        model_record.update(values)
        return model_record