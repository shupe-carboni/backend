import re
from app.adp.adp_models.model_series import ModelSeries, Fields, NoBasePrice
from app.db import Session


class MHCAB(ModelSeries):
    """Special Model series that is techincally classified as an accessory
    but it has features like a full product. For this reason, the material group
    is hard-coded to the Air Handler Accessories matieral group code."""

    text_len = (8,)
    regex = r"""
    (?P<series>MH)
    (?P<acc_type>[C|F])
    (?P<airflow_dir>[D|U])
    (?P<door_type>[L|S])
    (?P<top>[O|S])
    (?P<height>18|20|23|24|28|30|36|40)
    """

    # for heights that aren't an int
    height_mapping = {23: 23.25, 30: 30.5, 40: 40.25}
    weight_mapping = {
        24: 85,
        36: 85,
        48: 85,
        60: 100,
    }
    misc_nomen_mapping = {
        "C": "Coil Cabinet",
        "F": "Filter Grille",
        "D": "Downflow",
        "U": "Upflow",
        "L": "Louvered",
        "S": "Solid",
        "O": "Open",
    }

    def __init__(
        self, session: Session, re_match: re.Match, db: Session, *args, **kwargs
    ):
        super().__init__(session, re_match, db, *args, **kwargs)
        self.width = 19.8
        self.pallet_qty = 4
        height = int(self.attributes["height"])
        self.height: int | float = self.height_mapping.get(height, height)
        self.configuration = self.misc_nomen_mapping[self.attributes["airflow_dir"]]
        self.door = self.misc_nomen_mapping[self.attributes["door_type"]]
        self.acc_type = self.misc_nomen_mapping[self.attributes["acc_type"]]
        if self.acc_type == self.misc_nomen_mapping["F"]:
            self.top = None
            self.depth = None
        else:
            self.top = self.misc_nomen_mapping[self.attributes["top"]]
            self.depth = 23.5
        self.mat_grp = "SC"  # Accessory - AH
        self.zero_disc_price = self.calc_zero_disc_price() / 100

    def category(self) -> str:
        return f"Manufactured Home Electric Furnace - Coil Cabinets"

    def calc_zero_disc_price(self) -> int:
        model = str(self)
        params = dict(
            key_mode=self.KeyMode.EXACT.value,
            key_param=[model],
            series="MHCAB",
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
            Fields.PALLET_QTY.value: self.pallet_qty,
            Fields.WIDTH.value: self.width,
            Fields.DEPTH.value: self.depth,
            Fields.HEIGHT.value: self.height,
            Fields.CONFIGURATION.value: self.configuration,
            Fields.DOOR.value: self.door,
            Fields.ACCESSORY_TYPE.value: self.acc_type,
            Fields.TOP.value: self.top,
            Fields.ZERO_DISCOUNT_PRICE.value: self.zero_disc_price,
        }
        model_record.update(values)
        return model_record
