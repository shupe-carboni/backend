import re
from app.adp.adp_models.model_series import ModelSeries, Fields, NoBasePrice
from app.db import Session


class AMH(ModelSeries):
    text_len = (12,)
    regex = r"""
    (?P<series>AMH)
    (?P<motor>E)
    (?P<tonnage>[2|3|4|5])
    (?P<config>D)
    (?P<heat>00|05|07|10|12|15|20)
    (?P<line_conn>S|B)
    (?P<voltage>1|2)
    (?P<cab_color>N)
    (?P<revision>\d)
    """

    cfm_mapping = {
        2: "600-800",
        24: "600-800",
        3: "900-1100",
        36: "900-1100",
        4: "1200-1400",
        48: "1200-1400",
        5: "1200-1800",
        60: "1200-1800",
    }
    weight_mapping = {
        24: 85,
        36: 85,
        48: 85,
        60: 100,
    }
    voltage_mapping = {
        1: "120 V",
        2: "208/240 V",
    }

    def __init__(
        self, session: Session, re_match: re.Match, db: Session, *args, **kwargs
    ):
        super().__init__(session, re_match, db, *args, **kwargs)
        self.tonnage = int(self.attributes["tonnage"]) * 12
        self.cfm = self.cfm_mapping[self.tonnage]
        self.heat = self.kw_heat[int(self.attributes["heat"])]
        self.width = 19.8
        self.height = 33
        self.depth = 23.5
        self.pallet_qty = 4
        self.weight = self.weight_mapping[self.tonnage]
        self.motor = self.motors[self.attributes["motor"]]
        mask = self.mat_grps["series"] == self.__series_name__()
        self.mat_grp = self.mat_grps.loc[mask, "mat_grp"].item()
        self.voltage = self.voltage_mapping[int(self.attributes["voltage"])]
        self.zero_disc_price = self.calc_zero_disc_price() / 100

    def category(self) -> str:
        return f"Manufactured Home Electric Furnace - {self.voltage}"

    def calc_zero_disc_price(self) -> int:
        model = str(self)
        params = dict(
            key_mode=self.KeyMode.EXACT.value,
            key_param=[model],
            series="AMH",
            vendor_id="adp",
            customer_id=self.customer_id,
        )
        sql = self.pricing_sql
        price = self.db.execute(self.session, sql, params).one_or_none()
        if not price:
            raise NoBasePrice(
                "No record found in the price table with this model number."
            )
        else:
            _, price, self.eff_date = price
        return price

    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.EFFECTIVE_DATE.value: str(self.eff_date),
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
            Fields.HEAT.value: self.heat,
            Fields.CFM.value: self.cfm,
            Fields.VOLTAGE.value: self.voltage,
            Fields.ZERO_DISCOUNT_PRICE.value: self.zero_disc_price,
        }
        model_record.update(values)
        return model_record
