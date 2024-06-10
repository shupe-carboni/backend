import re
from app.adp.adp_models.model_series import ModelSeries, Fields
from app.db import ADP_DB, Session


class S(ModelSeries):
    text_len = (8, 9)
    regex = r"""
        (?P<series>S)
        (?P<mat>[M|K|L])
        (?P<scode>\d)
        (?P<meter>\d)
        (?P<ton>\d{2})
        (?P<heat>(\d{2}|(XX)))
        (?P<rds>[N|R]?)
    """
    weight_by_material = {"K": "weight_cu", "L": "weight_cu", "M": "weight_al"}

    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        self.tonnage = int(self.attributes["ton"])
        weight_col = self.weight_by_material[self.attributes["mat"]]
        specs_sql = f"""
            SELECT width, depth, height, {weight_col}
            FROM s_dims
            WHERE tonnage = :ton;
        """
        params = dict(ton=self.tonnage)
        specs = (
            ADP_DB.execute(session=session, sql=specs_sql, params=params)
            .mappings()
            .one()
        )
        self.min_qty = 4
        self.width = specs["width"]
        self.depth = specs["depth"]
        self.height = specs["height"]
        self.weight = specs[weight_col]
        self.motor = (
            "PSC Motor" if int(self.attributes["ton"]) % 2 == 0 else "ECM Motor"
        )
        self.metering = self.metering_mapping[int(self.attributes["meter"])]
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps["series"] == self.__series_name__())
            & (self.mat_grps["mat"].str.contains(self.attributes["mat"])),
            "mat_grp",
        ].item()
        self.ratings_ac_txv = (
            rf"S{self.attributes['mat']}"
            rf"{self.attributes['scode']}\(6,9\){self.tonnage}"
        )
        self.ratings_hp_txv = (
            rf"S{self.attributes['mat']}" rf"{self.attributes['scode']}9{self.tonnage}"
        )
        self.ratings_piston = (
            rf"S{self.attributes['mat']}"
            rf"{self.attributes['scode']}\(1,2\){self.tonnage}"
        )
        self.ratings_field_txv = (
            rf"S{self.attributes['mat']}"
            rf"{self.attributes['scode']}\(1,2\){self.tonnage}\+TXV"
        )
        self.is_flex_coil = True if self.attributes.get("rds") else False

    def category(self) -> str:
        motor = self.motor
        value = f"Wall Mount Air Handlers - {motor}"
        if self.is_flex_coil:
            value += " - FlexCoil"
        return value

    def load_pricing(self) -> tuple[int, dict[str, int]]:
        # NOTE the ~ operator compares the parameter str to the regex
        # patterns in the column
        pricing_sql = f"""
            SELECT "{self.attributes['heat']}"
            FROM pricing_s_series
            WHERE :model_number ~ model;
        """
        params = dict(model_number=str(self))
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
        result += adders_.get(self.attributes["ton"], 0)
        if self.is_flex_coil:
            result += 10
        return result

    def set_heat(self):
        try:
            self.heat = int(self.attributes["heat"])
            self.heat = self.kw_heat[self.heat]
        except Exception as e:
            self.heat = "Error"
            print(e)

    def record(self) -> dict:
        self.set_heat()
        model_record = super().record()
        values = {
            Fields.MODEL_NUMBER.value: str(self),
            Fields.CATEGORY.value: self.category(),
            Fields.MPG.value: self.mat_grp,
            Fields.SERIES.value: self.__series_name__(),
            Fields.TONNAGE.value: self.tonnage,
            Fields.MIN_QTY.value: self.min_qty,
            Fields.WIDTH.value: self.width,
            Fields.DEPTH.value: self.depth,
            Fields.HEIGHT.value: self.height,
            Fields.WEIGHT.value: self.weight,
            Fields.MOTOR.value: self.motor,
            Fields.METERING.value: self.metering,
            Fields.HEAT.value: self.heat,
            Fields.ZERO_DISCOUNT_PRICE.value: self.calc_zero_disc_price(),
            Fields.RATINGS_AC_TXV.value: self.ratings_ac_txv,
            Fields.RATINGS_HP_TXV.value: self.ratings_hp_txv,
            Fields.RATINGS_PISTON.value: self.ratings_piston,
            Fields.RATINGS_FIELD_TXV.value: self.ratings_field_txv,
        }
        model_record.update(values)
        return model_record
