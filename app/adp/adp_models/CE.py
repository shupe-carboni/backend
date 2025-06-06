import re
from app.adp.adp_models.model_series import ModelSeries, Fields, Cabinet
from app.adp.utils.validator import Validator, ParsingModes
from app.db import DB_V2, Session, Database


class CE(ModelSeries):
    text_len = (11, 12)
    regex = r"""
        (?P<series>CE)
        (?P<config>[H|M|P|S|V])
        (?P<ton>\d{2})
        (?P<width_height>\d{2})
        (?P<mat>[E|G|H|D|P])
        (?P<scode>\d{2}|\d\D)
        (?P<metering>[1|9|A|B])
        (?P<rds>[N|R]?)
    """
    ce_configurations = {
        "H": ("Horizontal", "CR"),
        "M": ("Mobile Home", "CO"),
        "P": ("Multi-position", "CM"),
        "S": ("Slab", "CD"),
        "V": ("Vertical", "CA"),
    }

    def __init__(
        self, session: Session, re_match: re.Match, db: Database, *args, **kwargs
    ):
        super().__init__(session, re_match, db, *args, **kwargs)
        dims_sql = """
            SELECT adp_model, width, depth, height, length, weight,
                pallet_qty
            FROM adp_ce_dims
            WHERE model = :model ;
        """
        params = dict(model=str(self))
        specs = (
            DB_V2.execute(session=session, sql=dims_sql, params=params).mappings().one()
        )
        specs = {k: v for k, v in specs.items() if v}
        self.configuration = self.ce_configurations[self.attributes["config"]]
        self.mat_grp = self.configuration[1]
        self.cabinet_config = Cabinet.PAINTED
        self.pallet_qty = specs["pallet_qty"]
        self.height = specs["height"]
        self.width = specs["width"]
        self.weight = specs["weight"]
        self.real_model = specs["adp_model"]
        self.tonnage = int(self.attributes["ton"])
        rds_option = self.attributes.get("rds")
        self.rds_factory_installed = False
        self.rds_field_installed = False
        match rds_option:
            case "R":
                self.rds_factory_installed = True
            case "N":
                self.rds_field_installed = True
        metering = self.attributes["metering"]
        try:
            metering = int(metering)
            if self.rds_field_installed or self.rds_factory_installed:
                metering = -metering
        except ValueError:
            pass
        self.metering = self.metering_mapping[metering]
        match self.attributes["config"]:
            case "H":
                from app.adp.adp_models.V import V

                self.length = specs["length"]
                self.depth = None
                real_model_obj = V
            case "M":
                from app.adp.adp_models.MH import MH

                self.length = None
                self.depth = specs["depth"]
                real_model_obj = MH
            case "P":
                from app.adp.adp_models.HE import HE

                self.length = None
                self.depth = specs["depth"]
                real_model_obj = HE
            case "V":
                from app.adp.adp_models.HE import HE

                self.length = None
                self.depth = specs["depth"]
                real_model_obj = HE
            case "S":
                from app.adp.adp_models.HH import HH

                self.length = None
                self.depth = specs["depth"]
                real_model_obj = HH

        strat = (
            ParsingModes.BASE_PRICE_FUTURE
            if self.use_future
            else ParsingModes.BASE_PRICE
        )

        self.real_model_obj = Validator(
            session, self.real_model, real_model_obj
        ).is_model(strat)
        self.zero_disc_price = self.real_model_obj.calc_zero_disc_price() / 100
        self.ratings_ac_txv = (
            rf"CE\(([P|V|S|H|M],){{1:4}}[P|V|S|H|M]\)"
            rf"{self.tonnage}{self.attributes['width_height']}"
            rf"{self.attributes['mat']}{self.attributes['scode']}"
            r"\*"
        )
        self.ratings_hp_txv = self.ratings_ac_txv
        self.ratings_piston = None
        self.ratings_field_txv = None

    def record(self) -> dict:
        model_record = super().record()
        values = {
            Fields.EFFECTIVE_DATE.value: str(self.real_model_obj.eff_date),
            Fields.MODEL_NUMBER.value: self.real_model,
            Fields.PRIVATE_LABEL.value: str(self),
            Fields.CATEGORY.value: self.real_model_obj.category(),
            Fields.SERIES.value: self.real_model_obj.__series_name__(),
            Fields.TONNAGE.value: self.tonnage,
            Fields.TOP_LEVEL_CLASS.value: self.top_level_category,
            Fields.MPG.value: self.mat_grp,
            Fields.PALLET_QTY.value: self.pallet_qty,
            Fields.WIDTH.value: self.width,
            Fields.DEPTH.value: self.depth,
            Fields.LENGTH.value: self.length,
            Fields.HEIGHT.value: self.height,
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
