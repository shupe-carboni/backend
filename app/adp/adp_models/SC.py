import re
from app.adp.adp_models.model_series import ModelSeries, Fields, Cabinet
from app.db import DB_V2, Session, Database
from app.db.sql import queries


class SC(ModelSeries):
    text_len = (7,)
    regex = r"""
        (?P<series>S)
        (?P<ton>\d{2})
        (?P<mat>[R|L|H|S])
        (?P<width_height>\d{3})
        """
    configs = {
        "R": ("Right Hand Upflow", "Copper"),
        "L": ("Left Hand Upflow", "Copper"),
        "H": ("Horizontal", "Aluminum"),
        "S": ("Horizontal Slab", "Copper"),
    }

    def __init__(
        self, session: Session, re_match: re.Match, db: Database, *args, **kwargs
    ):
        super().__init__(session, re_match, db, *args, **kwargs)
        self.top_level_category = "Coils"  # NOTE matches DB class rank 1
        self.tonnage = int(self.attributes["ton"])
        specs_sql = """
            SELECT cased, width, depth, height, weight, pallet_qty
            FROM adp_sc_all_features
            WHERE ton = :ton
            AND :model ~ regex;
        """
        params = dict(ton=self.tonnage / 12, model=str(self))
        specs = (
            DB_V2.execute(session=session, sql=specs_sql, params=params)
            .mappings()
            .one()
        )
        self.metering = "Piston (R-410a or R-22)"
        width_height: int = int(self.attributes["width_height"])
        if width_height % 10 in (2, 7):
            self.width_height = width_height / 10 + 0.05
        else:
            self.width_height = width_height / 10
        config = self.configs[self.attributes["mat"]]
        self.config = config[0]
        self.material = config[1]
        self.pallet_qty = specs["pallet_qty"]
        self.depth = specs["depth"]
        self.width = specs["width"]
        self.height = specs["height"]
        self.cased = specs["cased"]
        self.cabinet_config: Cabinet = (
            Cabinet.EMBOSSED if self.cased else Cabinet.UNCASED
        )
        self.weight = specs["weight"]
        self.mat_grp = self.mat_grps.loc[
            (self.mat_grps["series"] == self.__series_name__())
            & (self.mat_grps["mat"].str.contains(self.attributes["mat"]))
            # self.cased is bool - the config column has bool only sometimes
            # so pandas keeps bools as literal strings of 'TRUE' and 'FALSE'
            & (self.mat_grps["config"] == str(self.cased).upper()),
            "mat_grp",
        ].item()
        self.ratings_ac_txv = None
        self.ratings_hp_txv = None
        self.ratings_piston = None
        self.ratings_field_txv = None
        self.zero_disc_price = self.calc_zero_disc_price() / 100

    def category(self) -> str:
        seer = "10 SEER"
        cased = "Uncased" if not self.cased else "Cased"
        config = self.config
        return f"{seer} {config} Service Coils - {cased}"

    def load_pricing(self, col: int) -> int:
        key_len = {
            "R": 4,
            "L": 4,
            "H": 7,
            "S": 4,
        }
        key = f"{str(self)[:(key_len[self.attributes['mat']])]}_{col}"
        params = dict(
            key_mode=self.KeyMode.REGEX.value,
            key_param=[key],
            series="SC",
            vendor_id="adp",
            customer_id=self.customer_id,
        )
        _, price, self.eff_date = self.db.execute(
            session=self.session, sql=self.pricing_sql, params=params
        ).one()
        return int(price)

    def calc_zero_disc_price(self) -> int:
        match self.attributes["mat"]:
            case "R" | "L":
                column = int(self.cased)
            case "S":
                column = int(self.height > 19)
            case "H":
                column = int(True)
            case _:
                raise Exception("Invalid model configuration")
        return self.load_pricing(col=column)

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
            Fields.PALLET_QTY.value: self.pallet_qty,
            Fields.WIDTH.value: self.width,
            Fields.HEIGHT.value: self.height,
            Fields.DEPTH.value: self.depth,
            Fields.WEIGHT.value: self.weight,
            Fields.CABINET.value: self.cabinet_config.name.title(),
            Fields.METERING.value: self.metering,
            Fields.ZERO_DISCOUNT_PRICE.value: self.zero_disc_price,
            Fields.RATINGS_AC_TXV.value: self.ratings_ac_txv,
            Fields.RATINGS_HP_TXV.value: self.ratings_hp_txv,
            Fields.RATINGS_PISTON.value: self.ratings_piston,
            Fields.RATINGS_FIELD_TXV.value: self.ratings_field_txv,
        }
        model_record.update(values)
        return model_record
