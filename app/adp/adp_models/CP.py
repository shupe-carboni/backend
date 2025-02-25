import re
from app.adp.adp_models.model_series import (
    ModelSeries,
    Fields,
    PriceByCategoryAndKey,
    NoBasePrice,
)
from app.db import ADP_DB, Session, Database


class CP(ModelSeries):
    text_len = (15, 16)
    regex = r"""
        (?P<series>C)
        (?P<motor>[P|E])
        (?P<ton>\d{2})
        (?P<scode>\d{2})
        (?P<mat>[C|A])
        (?P<meter>[1|9|A|B|C])
        (?P<config>H)
        (?P<line_conn>[S|P])
        (?P<heat>\d{2})
        (?P<voltage>\d)
        (?P<cased>[U|C])
        (?P<revision_or_rds>[A|R])
        (?P<drain>R?)
    """
    metering_mapping_1 = {
        "A": "Piston (R-410A) w/ Access Port",
        "H": "Non-bleed HP-A/C TXV (R-410A)",
    }
    metering_mapping_2 = {
        -1: "Piston (R-410a) w/ Access Port",
        1: "Piston (R-454B/R-32) w/ Access Port",
        -9: "Non-bleed HP-A/C TXV (R-410a)",
        9: "Non-bleed HP-A/C TXV (R-410a)",
        "A": "Non-bleed HP-A/C TXV (R-454B)",
        "B": "Non-bleed HP-A/C TXV (R-32)",
        "C": "Bleed HP-A/C TXV (R-454B)",
    }

    def __init__(self, session: Session, re_match: re.Match, db: Database):
        super().__init__(session, re_match, db)
        self.pallet_qty = 8
        self.cased = self.attributes.get("cased") == "C"
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
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps["series"] == self.__series_name__()), "mat_grp"
        ].item()
        self.tonnage = int(self.attributes["ton"])
        self.ratings_ac_txv = (
            rf"C{self.attributes['motor']}"
            rf"{self.tonnage}{self.attributes['scode']}"
            rf"{self.attributes['mat']}\*\+TXV"
        )
        self.ratings_hp_txv = self.ratings_ac_txv
        self.ratings_piston = (
            rf"C{self.attributes['motor']}"
            rf"{self.tonnage}{self.attributes['scode']}"
            rf"{self.attributes['mat']}1"
        )
        self.ratings_field_txv = self.ratings_ac_txv
        self.rds_factory_installed = False
        match self.attributes.get("revision_or_rds"):
            case "R":
                self.rds_factory_installed = True
                try:
                    metering = int(self.attributes["meter"])
                except ValueError:
                    metering = self.attributes["meter"]
            case "A" if self.attributes["meter"] not in ("1", "9"):
                raise Exception(
                    "invalid model. Revision 'A' is reserved for "
                    "R-410a legacy models, metering 1 or 9. Nomenclature changes"
                    " invalidated the A/H nomenclature for metering on this series."
                )
            case "A" if self.attributes["meter"] in ("1", "9"):
                metering = -int(self.attributes["meter"])

        self.metering = self.metering_mapping_2[metering]
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
        if self.rds_factory_installed:
            value += " - A2L"
        else:
            value += " - R410a"
        if self.attributes.get("drain"):
            value += " - Right Hand Drain"
        return value

    def load_pricing(self) -> tuple[int, PriceByCategoryAndKey]:
        sql = f"""
            SELECT price
            FROM vendor_product_series_pricing
            WHERE key = :model 
            AND vendor_id = 'adp'
            AND series = 'CP';
        """
        model = str(self)
        params = dict(model=model)
        result = self.db.execute(
            session=self.session, sql=sql, params=params
        ).scalar_one_or_none()
        if not result:
            raise NoBasePrice(
                "No record found in the price table with this model number."
            )
        return int(result), self.get_adders()

    def get_zero_disc_price(self) -> int:
        base_price, adders = self.load_pricing()
        result = base_price
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
