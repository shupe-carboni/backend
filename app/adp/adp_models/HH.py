import re
from app.adp.adp_models.model_series import (
    ModelSeries,
    Fields,
    Cabinet,
    PriceByCategoryAndKey,
)
from app.db import ADP_DB, Session


class HH(ModelSeries):
    text_len = (18, 17)
    regex = r"""
        (?P<paint>H)
        (?P<mat>H)
        (?P<scode>\d{2})
        (?P<meter>[\d|A|B])
        (?P<ton>\d{2})
        (?P<depth>A)
        (?P<width>\d{3})
        (?P<notch>A)
        (?P<height>\d{2})
        (?P<config>\d{2})
        (?P<option>(AP)|[R|N])
    """

    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        specs_sql = """
            SELECT pallet_qty, "WEIGHT"
            FROM hh_weights_pallet
            WHERE "SC_1" = :scode;
        """
        params = dict(scode=int(self.attributes["scode"]))
        specs = (
            ADP_DB.execute(session=self.session, sql=specs_sql, params=params)
            .mappings()
            .one()
        )
        self.cabinet_config = Cabinet.EMBOSSED
        width = int(self.attributes["width"])
        self.width = width // 10 + (5 / 8) + 4 + (3 / 8)
        self.depth = 10
        self.height = int(self.attributes["height"]) + 0.25 + 1.5
        self.material = "Copper"
        self.pallet_qty = specs["pallet_qty"]
        self.weight = specs["WEIGHT"]
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps["series"] == self.__series_name__()), "mat_grp"
        ].item()
        self.tonnage = int(self.attributes["ton"])
        self.ratings_ac_txv = rf"HH{self.attributes['scode']}(\(6,9\)|\*){self.tonnage}"
        self.ratings_hp_txv = rf"HH{self.attributes['scode']}(9|\*){self.tonnage}"
        self.ratings_piston = rf"HH{self.attributes['scode']}(\(1,2\)|\*){self.tonnage}"
        self.ratings_field_txv = (
            rf"HH{self.attributes['scode']}(\(1,2\)|\*){self.tonnage}\+TXV"
        )
        rds_option = self.attributes.get("option")
        self.rds_factory_installed = False
        self.rds_field_installed = False
        match rds_option:
            case "R":
                self.rds_factory_installed = True
            case "N":
                self.rds_field_installed = True
        metering = self.attributes["meter"]
        try:
            metering = int(metering)
            if self.rds_field_installed or self.rds_factory_installed:
                metering = -metering
        except ValueError:
            pass
        self.metering = self.metering_mapping[metering]
        self.zero_disc_price = self.calc_zero_disc_price()

    def category(self) -> str:
        value = "Horizontal Slab Coils"
        if self.rds_field_installed or self.rds_factory_installed:
            value += " - A2L"
        return value

    def load_pricing(self) -> tuple[int, PriceByCategoryAndKey]:

        pricing_sql = """
            SELECT price
            FROM pricing_hh_series
            WHERE slab = :slab;
        """
        params = dict(slab=self.attributes["scode"])
        pricing: int = ADP_DB.execute(
            session=self.session, sql=pricing_sql, params=params
        ).scalar_one()

        return pricing, self.get_adders()

    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = self.load_pricing()
        result = pricing_ + adders_["metering"].get(self.attributes["meter"], 0)
        result += adders_["RDS"].get(self.attributes["option"], 0)
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
