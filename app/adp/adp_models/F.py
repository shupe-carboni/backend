import re
from app.adp.adp_models.model_series import ModelSeries, Fields
from app.db import ADP_DB, Session


class F(ModelSeries):
    text_len = (13, 14)
    regex = r"""
        (?P<series>F)
        (?P<motor>[C|E])
        (?P<config>M)
        (?P<scode>\D{2}\d|\D\d{2})
        (?P<meter>\d)
        (?P<ton>\d{2})
        (?P<line_conn>[S|B])
        (?P<heat>\d{2})
        (?P<voltage>\d)
        (?P<rds>[N|R]?)
        """

    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        self.tonnage = int(self.attributes["ton"])
        specs_sql = """
            SELECT height, depth, width, weight
            FROM f_dims
            WHERE tonnage = :tonnage;
        """
        params = dict(tonnage=self.tonnage)
        specs = (
            ADP_DB.execute(session=session, sql=specs_sql, params=params)
            .mappings()
            .one()
        )
        self.min_qty = 4
        self.width = specs["width"]
        self.depth = specs["depth"]
        self.height = specs["height"]
        self.weight = specs["weight"]
        self.motor = self.motors[self.attributes["motor"]]
        self.metering = self.metering_mapping[int(self.attributes["meter"])]
        self.heat = self.kw_heat[int(self.attributes["heat"])]
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps["series"] == self.__series_name__())
            & (
                self.mat_grps["mat"].str.contains(
                    re.sub(r"\d+", "", self.attributes["scode"])
                )
            ),
            "mat_grp",
        ].item()
        s_code = self.attributes["scode"]
        self.s_code_mat = s_code[0] if s_code[0] in ("E", "G") else s_code[:2]
        self.ratings_ac_txv = (
            rf"""F,P{self.attributes['motor']}\*{s_code}\(6,9\){self.tonnage}"""
        )
        self.ratings_hp_txv = (
            rf"""F,P{self.attributes['motor']}\*{s_code}9{self.tonnage}"""
        )
        self.ratings_piston = (
            rf"""F,P{self.attributes['motor']}\*{s_code}\(1,2\){self.tonnage}"""
        )
        self.ratings_field_txv = (
            rf"""F,P{self.attributes['motor']}\*{s_code}\(1,2\){self.tonnage}\+TXV"""
        )
        self.is_flex_coil = True if self.attributes.get("rds") else False
        self.zero_disc_price = self.calc_zero_disc_price()

    def load_pricing(self) -> tuple[dict[str, int], dict[str, int]]:

        pricing_sql = """
            SELECT base, "05", "07", "10", "15", "20"
            FROM pricing_f_series
            WHERE :slab ~ slab
            AND tonnage = :ton;
        """
        # NOTE the ~ operator in Postgres checks that :slab matches regex
        # values contained in the column "slab"
        params = dict(slab=self.attributes["scode"], ton=self.tonnage)
        pricing = (
            ADP_DB.execute(session=self.session, sql=pricing_sql, params=params)
            .mappings()
            .one_or_none()
        )

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

    def category(self) -> str:
        orientation = "Multiposition"
        motor = self.motor
        value = f"Low Profile {orientation} Air Handlers - {motor}"
        if self.is_flex_coil:
            value += " - FlexCoil"
        return value

    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = self.load_pricing()
        heat: str = self.attributes["heat"]
        if heat != "00":
            try:
                result = pricing_[heat]
            except:
                raise self.NoBasePrice
        else:
            result = pricing_["base"]
        result += adders_.get(self.attributes["voltage"], 0)
        if heat == "05" and self.attributes["line_conn"] == "B":
            result += adders_.get(self.attributes["line_conn"], 0)
        result += (
            adders_.get(self.attributes["ton"], 0)
            if self.attributes["motor"] == "E"
            else 0
        )
        result += adders_.get(self.attributes["meter"], 0)
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
            Fields.MIN_QTY.value: self.min_qty,
            Fields.WIDTH.value: self.width,
            Fields.DEPTH.value: self.depth,
            Fields.HEIGHT.value: self.height,
            Fields.WEIGHT.value: self.weight,
            Fields.MOTOR.value: self.motor,
            Fields.METERING.value: self.metering,
            Fields.HEAT.value: self.heat,
            Fields.ZERO_DISCOUNT_PRICE.value: self.zero_disc_price,
            Fields.RATINGS_AC_TXV.value: self.ratings_ac_txv,
            Fields.RATINGS_HP_TXV.value: self.ratings_hp_txv,
            Fields.RATINGS_PISTON.value: self.ratings_piston,
            Fields.RATINGS_FIELD_TXV.value: self.ratings_field_txv,
        }
        model_record.update(values)
        return model_record
