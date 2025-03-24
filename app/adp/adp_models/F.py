import re
from app.adp.adp_models.model_series import ModelSeries, Fields, PriceByCategoryAndKey
from app.db import ADP_DB, Session, Database


class F(ModelSeries):
    text_len = (13, 14)
    regex = r"""
        (?P<series>F)
        (?P<motor>[C|E])
        (?P<config>M)
        (?P<scode>\D{2}\d|\D\d{2})
        (?P<meter>[\d|A|B])
        (?P<ton>\d{2})
        (?P<line_conn>[S|B])
        (?P<heat>\d{2})
        (?P<voltage>\d)
        (?P<revision>[A]?)
        (?P<rds>[R]?)
        """

    def __init__(
        self, session: Session, re_match: re.Match, db: Database, *args, **kwargs
    ):
        super().__init__(session, re_match, db, *args, **kwargs)
        if not any([self.attributes.get("revision"), self.attributes.get("rds")]):
            raise Exception(
                "Invalid Model Number. Legacy R410a models now have a "
                "trailing revision number."
            )
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
        rds_option = self.attributes.get("rds")
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
            if self.rds_factory_installed:
                metering = -metering
        except ValueError:
            pass
        a2l_coil = self.rds_factory_installed or self.rds_field_installed
        if a2l_coil:
            self.ratings_ac_txv = (
                rf"""F{self.attributes['motor']}\*{s_code}\*{self.tonnage}\+TXV"""
            )
            self.ratings_piston = (
                rf"""F{self.attributes['motor']}\*{s_code}1{self.tonnage}"""
            )
            self.ratings_hp_txv = self.ratings_field_txv = self.ratings_ac_txv
        else:
            self.ratings_ac_txv = (
                rf"""F,P{self.attributes['motor']}\*{s_code}(\(6,9\)){self.tonnage}"""
            )
            self.ratings_hp_txv = (
                rf"""F,P{self.attributes['motor']}\*{s_code}(9){self.tonnage}"""
            )
            self.ratings_piston = (
                rf"""F,P{self.attributes['motor']}\*{s_code}(\(1,2\)){self.tonnage}"""
            )
            self.ratings_field_txv = rf"""F,P{self.attributes['motor']}\*{s_code}(\(1,2\)){self.tonnage}\+TXV"""
        self.metering = self.metering_mapping[metering]
        self.zero_disc_price = self.calc_zero_disc_price() / 100

    def load_pricing(self) -> tuple[dict[str, int], PriceByCategoryAndKey]:

        # NOTE the ~ operator in Postgres checks that :slab matches regex
        # values contained in the column "slab". The selection based on key
        # ignores the key suffix that denotes the heat kit so that it grabs them all
        if self.use_future:
            pricing_sql = """
                SELECT key, future.price
                FROM vendor_product_series_pricing_future AS future
                JOIN vendor_product_series_pricing
                ON future.price_id = vendor_product_series_pricing.id
                AND :key ~ SUBSTRING(key FROM '^[^_]*_[^_]*_')
                AND vendor_id = 'adp'
                AND series = 'F';
            """
        else:
            pricing_sql = """
                SELECT key, price
                FROM vendor_product_series_pricing
                WHERE :key ~ SUBSTRING(key FROM '^[^_]*_[^_]*_')
                AND vendor_id = 'adp'
                AND series = 'F';
            """
        key = f"{self.tonnage}_{self.attributes['scode']}_"
        params = dict(key=key)
        pricing = (
            self.db.execute(session=self.session, sql=pricing_sql, params=params)
            .mappings()
            .fetchall()
        )
        pricing_reorganized = dict()
        for row in pricing:
            option = row["key"].split("_")[-1]
            pricing_reorganized[option] = row["price"]
        return pricing_reorganized, self.get_adders()

    def category(self) -> str:
        orientation = "Multiposition"
        motor = self.motor
        value = f"Low Profile {orientation} Air Handlers - {motor}"
        if self.rds_field_installed:
            value += " - FlexCoil"
        elif self.rds_factory_installed:
            value += " - A2L"
        else:
            value += " - R410a"
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
        result += adders_["voltage"].get(self.attributes["voltage"], 0)
        if heat == "05" and self.attributes["line_conn"] == "B":
            result += adders_["line_conn"].get(self.attributes["line_conn"], 0)
        result += (
            adders_["tonnage"].get(self.attributes["ton"], 0)
            if self.attributes["motor"] == "E"
            else 0
        )
        result += adders_["metering"].get(self.attributes["meter"], 0)
        result += adders_["RDS"].get(self.attributes.get("rds"), 0)
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
