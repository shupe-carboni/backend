import re
from app.adp.adp_models.model_series import ModelSeries, Fields, PriceByCategoryAndKey
from app.db import ADP_DB, Session


class S(ModelSeries):
    text_len = (8, 9)
    regex = r"""
        (?P<series>S)
        (?P<mat>[M|K|L])
        (?P<scode>\d)
        (?P<meter>[\d|A|B])
        (?P<ton>\d{2})
        (?P<heat>(\d{2}|(XX)))
        (?P<revision>[A]?)
        (?P<rds>[R]?)
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
        if self.rds_factory_installed or self.rds_field_installed:
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

    def category(self) -> str:
        motor = self.motor
        value = f"Wall Mount Air Handlers - {motor}"
        if self.rds_field_installed:
            value += " - FlexCoil"
        elif self.rds_factory_installed:
            value += " - A2L"
        return value

    def load_pricing(self) -> tuple[int, PriceByCategoryAndKey]:
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
        return pricing, self.get_adders()

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
