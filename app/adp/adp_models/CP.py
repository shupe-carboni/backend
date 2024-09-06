import re
from app.adp.adp_models.model_series import ModelSeries, Fields
from app.db import ADP_DB, Session


class NoBasePrice(Exception): ...


class CP(ModelSeries):
    text_len = (14, 13)
    regex = r"""
        (?P<series>C)
        (?P<motor>[P|E])
        (?P<ton>\d{2})
        (?P<scode>\d{2})
        (?P<mat>[C|A])
        (?P<meter>[A|H])
        (?P<config>H)
        (?P<line_conn>[S|P])
        (?P<heat>\d{2})
        (?P<voltage>\d)
        (?P<option>C?)
        (?P<drain>R?)
        (?P<rds>[N|R]?)
    """
    metering_mapping_ = {
        "A": "Piston (R-410A) w/ Access Port",
        "H": "Non-bleed HP-A/C TXV (R-410A)",
    }

    def __init__(self, session: Session, re_match: re.Match):
        super().__init__(session, re_match)
        self.pallet_qty = 8
        self.cased = self.attributes.get("option") == "C"
        dims_sql = """
            SELECT weight, width, depth, height
            FROM cp_dims
            WHERE series = :series
            AND motor = :motor
            AND ton = :ton
            AND cased = :cased ;
        """
        params = dict(
            series=self.attributes["series"],
            motor=self.attributes["motor"],
            ton=self.attributes["ton"],
            cased=self.cased,
        )
        specs = (
            ADP_DB.execute(session=session, sql=dims_sql, params=params)
            .mappings()
            .one()
        )
        self.width = specs["width"]
        self.depth = specs["depth"]
        self.height = specs["height"]
        self.weight = specs["weight"]
        self.motor = self.motors[self.attributes["motor"]]
        self.metering = self.metering_mapping_[self.attributes["meter"]]
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps["series"] == self.__series_name__()), "mat_grp"
        ].item()
        self.tonnage = int(self.attributes["ton"])
        self.ratings_ac_txv = (
            rf"C{self.attributes['motor']}"
            rf"{self.tonnage}{self.attributes['scode']}"
            rf"{self.attributes['mat']}\+TXV"
        )
        self.ratings_hp_txv = self.ratings_ac_txv
        self.ratings_piston = (
            rf"C{self.attributes['motor']}"
            rf"{self.tonnage}{self.attributes['scode']}"
            rf"{self.attributes['mat']}"
        )
        self.ratings_field_txv = self.ratings_ac_txv
        rds_option = self.attributes.get("rds")
        self.rds_factory_installed = False
        self.rds_field_installed = False
        match rds_option:
            case "R":
                self.rds_factory_installed = True
            case "N":
                self.rds_field_installed = True
        self.zero_disc_price = self.get_zero_disc_price()
        try:
            self.heat = int(self.attributes["heat"])
            self.heat = self.kw_heat[self.heat]
        except Exception as e:
            self.heat = "error"

    def category(self) -> str:
        material = self.material_mapping[self.attributes["mat"]]
        motor = self.motor
        cased = "Uncased" if not self.cased else "Cased"
        value = f"Soffit Mount {cased} Air Handlers - {material} - {motor}"
        if self.rds_field_installed:
            value += " - FlexCoil"
        elif self.rds_factory_installed:
            value += " - A2L"
        return value

    def load_pricing(self) -> tuple[int, dict[str, int]]:
        sql = f"""
            SELECT price
            FROM pricing_cp_series
            WHERE "{self.attributes['mat']}" = :model ;
        """
        model = str(self)
        if self.attributes.get("rds"):
            model = model[:-1]
        params = dict(model=model)
        result = ADP_DB.execute(
            session=self.session, sql=sql, params=params
        ).scalar_one_or_none()
        if not result:
            raise NoBasePrice
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
        return int(result), adders

    def get_zero_disc_price(self) -> int:
        base_price, adders = self.load_pricing()
        result = base_price + adders.get(self.attributes.get("rds"), 0)
        return result

    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.MODEL_NUMBER.value: str(self),
            Fields.CATEGORY.value: self.category(),
            Fields.SERIES.value: self.__series_name__(),
            Fields.MPG.value: self.mat_grp,
            Fields.TONNAGE.value: self.tonnage,
            Fields.PALLET_QTY.value: self.pallet_qty,
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
