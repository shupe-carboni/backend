import re
from app.adp.adp_models.model_series import ModelSeries, Fields, PriceByCategoryAndKey
from app.db import DB_V2, Session, Database, CACHE
from app.db.sql import queries


class B(ModelSeries):
    text_len = (13, 14)
    regex = r"""
        (?P<series>B)
        (?P<motor>[C|V])
        (?P<hpanpos>[R|O])
        (?P<config>M)
        (?P<scode>\D\d|(00))
        (?P<meter>[\d|A|B])
        (?P<ton>\d{2})
        (?P<line_conn>S)
        (?P<heat>\d[0|P|N])
        (?P<voltage>\d)
        (?P<revision>[A]?)
        (?P<rds>[R]?)
        """

    class InvalidHeatOption(Exception): ...

    hydronic_heat = {
        "00": "no heat",
        "2P": "2 row hot water coil with pump assembly",
        "3P": "3 row hot water coil with pump assembly",
        "4P": "4 row hot water coil with pump assembly",
        "2N": "2 row hot water coil without pump assembly",
        "3N": "3 row hot water coil without pump assembly",
        "4N": "4 row hot water coil without pump assembly",
    }

    def __init__(
        self, session: Session, re_match: re.Match, db: Database, *args, **kwargs
    ):
        super().__init__(session, re_match, db, *args, **kwargs)
        self.top_level_category = "Air Handlers"  # NOTE matches DB class rank 1
        self.min_qty = 4
        cache_key = f'adp_b_specs_{self.attributes["ton"]}'
        specs = CACHE.get(cache_key)
        if not specs:
            dims_sql = """
                SELECT weight, height, depth, width
                FROM adp_b_dims
                WHERE tonnage = :tonnage;
            """
            specs = (
                DB_V2.execute(
                    session=session,
                    sql=dims_sql,
                    params={"tonnage": int(self.attributes["ton"])},
                )
                .mappings()
                .one_or_none()
            )
            CACHE.add_or_update(cache_key, specs)
        self.width = specs["width"]
        self.depth = specs["depth"]
        self.height = specs["height"]
        self.weight = specs["weight"]
        self.motor = self.motors[self.attributes["motor"]]
        self.heat = self.hydronic_heat[self.attributes["heat"]]
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
        metering = self.attributes["meter"]
        try:
            metering = int(metering)
            if self.rds_factory_installed:
                metering = -metering
        except ValueError:
            pass
        self.metering = self.metering_mapping[metering]
        a2l_coil = self.rds_factory_installed or self.rds_field_installed
        if a2l_coil:
            self.ratings_ac_txv = (
                rf"B{self.attributes['motor']}"
                rf"\*\*{self.attributes['scode']}"
                rf"\*{self.tonnage}+TXV"
            )
            self.ratings_hp_txv = self.ratings_field_txv = self.ratings_ac_txv
            self.ratings_piston = (
                rf"B{self.attributes['motor']}"
                rf"\*\*{self.attributes['scode']}"
                rf"1{self.tonnage}"
            )
        else:
            self.ratings_ac_txv = (
                rf"B{self.attributes['motor']}"
                rf"\*\*{self.attributes['scode']}"
                rf"(\(6,9\)){self.tonnage}"
            )
            self.ratings_hp_txv = (
                rf"B{self.attributes['motor']}"
                rf"\*\*{self.attributes['scode']}"
                rf"(9){self.tonnage}"
            )
            self.ratings_piston = (
                rf"B{self.attributes['motor']}"
                rf"\*\*{self.attributes['scode']}"
                rf"(\(1,2\)){self.tonnage}"
            )
            self.ratings_field_txv = (
                rf"B{self.attributes['motor']}"
                rf"\*\*{self.attributes['scode']}"
                rf"(\(1,2\)){self.tonnage}\+TXV"
            )
        self.zero_disc_price = self.calc_zero_disc_price() / 100

    def category(self) -> str:
        orientation = "Multiposition"
        motor = self.motor
        value = f"Hydronic {orientation} Air Handlers - {motor}"
        if self.rds_field_installed:
            value += " - FlexCoil"
        elif self.rds_factory_installed:
            value += " - A2L"
        else:
            value += "- R-410a"

        return value

    def load_pricing(self) -> tuple[dict[str, int], PriceByCategoryAndKey]:
        key_first_part = f"{self.tonnage}_{self.attributes['scode']}_"

        # NOTE normally I'd pass a tuple, but due to how the SQL uses typed arrays
        # (CARDINALITY and UNNEST), I'm passing a list so it becomes a CASTable array
        keys = [f"{key_first_part}{suffix}" for suffix in ("base", "2", "3", "4")]
        params = dict(
            key_mode=self.KeyMode.MEMBERSHIP.value,
            key_param=keys,
            series="B",
            vendor_id="adp",
            customer_id=self.customer_id,
        )
        pricing_records: tuple[dict[str, str | int]] = (
            self.db.execute(session=self.session, sql=self.pricing_sql, params=params)
            .mappings()
            .fetchall()
        )
        pricing = dict()
        for r in pricing_records:
            if r.get("key").endswith("base"):
                pricing["base"] = r.get("effective_price")
                pricing["effective_date"] = r.get("effective_date")
            elif r.get("key")[-1] in ("2", "3", "4"):
                pricing[r.get("key")[-1]] = r.get("effective_price")
                pricing["effective_date"] = r.get("effective_date")
        # CACHE.add_or_update(key_first_part, (pricing, self.get_adders()))
        return pricing, self.get_adders()

    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = self.load_pricing()
        heat: str = self.attributes["heat"]
        if not pricing_:
            raise self.NoBasePrice
        result = pricing_["base"]
        try:
            heat_option = pricing_[heat[0]] if heat != "00" else 0
            self.eff_date = pricing_["effective_date"]
        except Exception as e:
            raise self.InvalidHeatOption(e)
        result += heat_option
        result += adders_["metering"].get(self.attributes["meter"], 0)
        result += adders_["voltage"].get(self.attributes["voltage"], 0)
        result += adders_["heat"].get(self.attributes["heat"][-1], 0)
        result += adders_["motor"].get(self.attributes["motor"], 0)
        result += adders_["RDS"].get(self.attributes.get("rds"), 0)
        return result

    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.EFFECTIVE_DATE.value: str(self.eff_date),
            Fields.MODEL_NUMBER.value: str(self),
            Fields.CATEGORY.value: self.category(),
            Fields.TOP_LEVEL_CLASS.value: self.top_level_category,
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
