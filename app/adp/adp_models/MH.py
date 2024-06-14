import re
from app.adp.adp_models.model_series import ModelSeries, Fields, Cabinet
from app.db import ADP_DB, Session


class MH(ModelSeries):
    text_len = (7, 8)
    regex = r"""
        (?P<series>M)
        (?P<ton>\d{2})
        (?P<mat>E)
        (?P<scode>\d{2})
        (?P<meter>\d)
        (?P<rds>[R|N]?)
        """

    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        spec_sql = """
            SELECT "HEIGHT", "WEIGHT", "PALLET_QTY"
            FROM mh_pallet_weight_height
            WHERE "SC_1" = :slab;
        """
        specs = (
            ADP_DB.execute(
                session=self.session,
                sql=spec_sql,
                params=dict(slab=self.attributes["scode"]),
            )
            .mappings()
            .one()
        )
        self.cabinet_config = Cabinet.UNCASED
        self.metering = self.metering_mapping[int(self.attributes["meter"])]
        self.material = "Copper"
        self.width = 18
        self.depth = 19.5
        self.height = specs["HEIGHT"]
        self.pallet_qty = specs["PALLET_QTY"]
        self.weight = specs["WEIGHT"]
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps["series"] == self.__series_name__()), "mat_grp"
        ].item()
        self.tonnage = int(self.attributes["ton"])
        self.ratings_ac_txv = (
            rf"M{self.tonnage}{self.attributes['mat']}"
            rf"{self.attributes['scode']}[\(6,9\)|\*]"
        )
        self.ratings_hp_txv = (
            rf"M{self.tonnage}{self.attributes['mat']}"
            rf"{self.attributes['scode']}[9|\*]"
        )
        self.ratings_piston = (
            rf"M{self.tonnage}{self.attributes['mat']}"
            rf"{self.attributes['scode']}[\(1,2\)|\*]"
        )
        self.ratings_field_txv = (
            rf"M{self.tonnage}{self.attributes['mat']}"
            rf"{self.attributes['scode']}[\(1,2\)|\*]\+TXV"
        )
        self.is_flex_coil = True if self.attributes.get("rds") else False
        self.zero_disc_price = self.calc_zero_disc_price()

    def category(self) -> str:
        value = "Manufactured Housing Coils"
        if self.is_flex_coil:
            value += " - FlexCoil"
        return value

    def load_pricing(self) -> tuple[int, dict[str, int]]:
        pricing_sql = """
            SELECT price
            FROM pricing_mh_series
            WHERE slab = :slab;
        """
        params = dict(slab=self.attributes["scode"])
        pricing = ADP_DB.execute(
            session=self.session, sql=pricing_sql, params=params
        ).scalar_one()

        price_adders_sql = """
            SELECT key, price
            FROM price_adders
            WHERE series = :series;
        """
        params = dict(series=self.__series_name__())
        adders_ = (
            ADP_DB.execute(session=self.session, sql=price_adders_sql, params=params)
            .mappings()
            .all()
        )
        adders = dict()
        for adder in adders_:
            adders |= {adder["key"]: adder["price"]}
        return pricing, adders

    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = self.load_pricing()
        result = pricing_ + adders_.get(self.attributes["meter"], 0)
        if self.is_flex_coil:
            result += 10
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
