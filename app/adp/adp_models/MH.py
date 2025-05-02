import re
from app.adp.adp_models.model_series import (
    ModelSeries,
    Fields,
    Cabinet,
    PriceByCategoryAndKey,
)
from app.db import DB_V2, Session, Database
from app.db.sql import queries


class MH(ModelSeries):
    text_len = (7, 8)
    regex = r"""
        (?P<series>M)
        (?P<ton>\d{2})
        (?P<mat>[E|G])
        (?P<scode>\d{2})
        (?P<meter>[\d|A|B])
        (?P<rds>[R|N]?)
        """

    def __init__(
        self, session: Session, re_match: re.Match, db: Database, *args, **kwargs
    ):
        super().__init__(session, re_match, db, *args, **kwargs)
        spec_sql = """
            SELECT "HEIGHT", "WEIGHT", "PALLET_QTY"
            FROM adp_mh_pallet_weight_height
            WHERE "SC_1" = :slab;
        """
        specs = (
            DB_V2.execute(
                session=self.session,
                sql=spec_sql,
                params=dict(slab=self.attributes["scode"]),
            )
            .mappings()
            .one()
        )
        self.cabinet_config = Cabinet.UNCASED
        self.width = 18
        self.depth = 19.5
        self.height = specs["HEIGHT"]
        self.pallet_qty = specs["PALLET_QTY"]
        self.weight = specs["WEIGHT"]
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps["series"] == self.__series_name__()), "mat_grp"
        ].item()
        self.tonnage = int(self.attributes["ton"])
        rds_option = self.attributes.get("rds")
        self.rds_factory_installed = False
        self.rds_field_installed = False
        match rds_option:
            case "R":
                self.rds_factory_installed = True
            case "N":
                self.rds_field_installed = True
        a2l_coil = self.rds_factory_installed or self.rds_field_installed
        metering = self.attributes["meter"]
        try:
            metering = int(metering)
            if a2l_coil:
                metering = -metering
        except ValueError:
            pass
        self.metering = self.metering_mapping[metering]
        if not a2l_coil:
            self.ratings_ac_txv = (
                rf"M{self.tonnage}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(6,9\))"
            )
            self.ratings_hp_txv = (
                rf"M{self.tonnage}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(9)"
            )
            self.ratings_piston = (
                rf"M{self.tonnage}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(1,2\))"
            )
            self.ratings_field_txv = (
                rf"M{self.tonnage}{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(1,2\))\+TXV"
            )
        else:
            self.ratings_ac_txv = (
                rf"M{self.tonnage}{self.attributes['mat']}"
                rf"{self.attributes['scode']}\*\+TXV"
            )
            self.ratings_hp_txv = (
                rf"M{self.tonnage}{self.attributes['mat']}"
                rf"{self.attributes['scode']}\*\+TXV"
            )
            self.ratings_piston = (
                rf"M{self.tonnage}{self.attributes['mat']}"
                rf"{self.attributes['scode']}1"
            )
            self.ratings_field_txv = (
                rf"M{self.tonnage}{self.attributes['mat']}"
                rf"{self.attributes['scode']}\*\+TXV"
            )
        self.zero_disc_price = self.calc_zero_disc_price() / 100

    def category(self) -> str:
        value = "Manufactured Housing Coils"
        match self.attributes["mat"]:
            case "E":
                material = "Copper"
            case "G":
                material = "Aluminum"
            case _:
                raise Exception("Invalid Nomenclature for Coil Material")

        value += f" - {material}"

        if self.rds_field_installed or self.rds_factory_installed:
            value += " - A2L"
        else:
            value += "- R-410a"
        return value

    def load_pricing(self) -> tuple[int, PriceByCategoryAndKey]:
        params = dict(
            key_mode=self.KeyMode.EXACT.value,
            key_param=[self.attributes["scode"]],
            series="MH",
            vendor_id="adp",
            customer_id=self.customer_id,
        )
        _, pricing, self.eff_date = self.db.execute(
            session=self.session, sql=self.pricing_sql, params=params
        ).one()
        return pricing, self.get_adders()

    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = self.load_pricing()
        result = pricing_ + adders_["metering"].get(self.attributes["meter"], 0)
        result += adders_["RDS"].get(self.attributes.get("rds"), 0)
        return result

    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.EFFECTIVE_DATE.value: str(self.eff_date),
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
