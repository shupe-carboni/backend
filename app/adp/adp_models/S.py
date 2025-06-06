import re
from app.adp.adp_models.model_series import ModelSeries, Fields, PriceByCategoryAndKey
from app.db import DB_V2, Session, Database
from app.db.sql import queries


class S(ModelSeries):
    text_len = (8, 9)
    regex = r"""
        (?P<series>S)
        (?P<mat>[M|K|L])
        (?P<scode>\d)
        (?P<meter>[\d|A|B|C])
        (?P<ton>\d{2})
        (?P<heat>(\d{2}|(XX)))
        (?P<revision>[A]?)
        (?P<rds>[R]?)
    """
    weight_by_material = {"K": "weight_cu", "L": "weight_cu", "M": "weight_al"}

    def __init__(
        self, session: Session, re_match: re.Match, db: Database, *args, **kwargs
    ):
        super().__init__(session, re_match, db, *args, **kwargs)
        self.top_level_category = "Air Handlers"  # NOTE matches DB class rank 1
        self.tonnage = int(self.attributes["ton"])
        weight_col = self.weight_by_material[self.attributes["mat"]]
        specs_sql = f"""
            SELECT width, depth, height, {weight_col}
            FROM adp_s_dims
            WHERE tonnage = :ton;
        """
        params = dict(ton=self.tonnage)
        specs = (
            DB_V2.execute(session=session, sql=specs_sql, params=params)
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
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps["series"] == self.__series_name__())
            & (self.mat_grps["mat"].str.contains(self.attributes["mat"])),
            "mat_grp",
        ].item()
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
            self.ratings_piston = (
                rf"S{self.attributes['mat']}"
                rf"{self.attributes['scode']}1{self.tonnage}"
            )
            self.ratings_ac_txv = self.ratings_hp_txv = self.ratings_field_txv = (
                rf"S{self.attributes['mat']}"
                rf"{self.attributes['scode']}\*{self.tonnage}\+TXV"
            )
        else:
            self.ratings_ac_txv = (
                rf"S{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(6,9\)|\*){self.tonnage}"
            )
            self.ratings_hp_txv = (
                rf"S{self.attributes['mat']}"
                rf"{self.attributes['scode']}(9|\*){self.tonnage}"
            )
            self.ratings_piston = (
                rf"S{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(1,2\)|\*){self.tonnage}"
            )
            self.ratings_field_txv = (
                rf"S{self.attributes['mat']}"
                rf"{self.attributes['scode']}(\(1,2\)|\*){self.tonnage}\+TXV"
            )
        self.zero_disc_price = self.calc_zero_disc_price() / 100

    def category(self) -> str:
        motor = self.motor
        value = f"Wall Mount Air Handlers - {motor}"
        if self.rds_field_installed:
            value += " - FlexCoil"
        elif self.rds_factory_installed:
            value += " - A2L"
        else:
            value += "- R-410a"
        return value

    def load_pricing(self) -> tuple[int, PriceByCategoryAndKey]:
        key = f"{self.attributes['mat']}{self.attributes['scode']}_{self.attributes['heat']}"
        params = dict(
            key_mode=self.KeyMode.EXACT.value,
            key_param=[key],
            series="S",
            vendor_id="adp",
            customer_id=self.customer_id,
        )
        _, pricing, self.eff_date = self.db.execute(
            session=self.session, sql=self.pricing_sql, params=params
        ).one()
        return int(pricing), self.get_adders()

    def calc_zero_disc_price(self) -> int:
        pricing_, adders_ = self.load_pricing()
        result = pricing_ + adders_["metering"].get(self.attributes["meter"], 0)
        result += adders_["tonnage"].get(self.attributes["ton"], 0)
        result += adders_["RDS"].get(self.attributes.get("rds"), 0)
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
