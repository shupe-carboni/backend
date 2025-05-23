import re
from app.adp.adp_models.model_series import ModelSeries, Fields
from app.adp.utils.validator import Validator, ParsingModes
from app.db import DB_V2, Session, Database


class CF(ModelSeries):
    text_len = (10, 11, 12, 13)
    regex = r"""
        (?P<series>CF)
        (?P<application>[C|P|W])
        (?P<ton>\d{2})
        (?P<motor>[C|V|X])
        (?P<scode>\D{2}\d|\D\d{2})
        (?P<heat>\d{2})
        (?P<voltage>\d)
        (?P<revision>[A]?)
        (?P<rds>[R]?)
    """

    def __init__(
        self, session: Session, re_match: re.Match, db: Database, *args, **kwargs
    ):
        super().__init__(session, re_match, db, *args, **kwargs)
        self.tonnage = int(self.attributes["ton"])
        if rds := self.attributes.get("rds", ""):
            model_alias: str = str(self)[:-4] + rds
        else:
            model_alias: str = str(self)[:-3]

        model_mapping_sql = """
            SELECT model
            FROM adp_carrier_cf_label_mapping
            WHERE model_alias = :alias;
        """
        params = dict(alias=model_alias)
        actual_model = DB_V2.execute(
            session=session, sql=model_mapping_sql, params=params
        ).scalar_one()
        strat = (
            ParsingModes.BASE_PRICE_FUTURE
            if self.use_future
            else ParsingModes.BASE_PRICE
        )
        match self.attributes["application"]:
            case "C":
                from app.adp.adp_models.F import F

                self.model_obj = Validator(
                    db_session=session,
                    raw_text=actual_model,
                    model_series=F,
                ).is_model(strat)
                self._record = self.model_obj.record()
            case "P":
                from app.adp.adp_models.B import B

                self.model_obj = Validator(
                    db_session=session,
                    raw_text=actual_model,
                    model_series=B,
                ).is_model(strat)
                self._record = self.model_obj.record()
            case "W":
                from app.adp.adp_models.S import S

                self.model_obj = Validator(
                    db_session=session,
                    raw_text=actual_model,
                    model_series=S,
                ).is_model(strat)
                self._record = self.model_obj.record()
        self.ratings_ac_txv = (
            rf"{self.attributes['series']}"
            rf"{self.attributes['application']}"
            rf"{self.attributes['ton']}"
            rf"{self.attributes['motor']}"
            rf"{self.attributes['scode']}"
        )
        self.ratings_hp_txv = self.ratings_ac_txv

    def record(self) -> dict:
        self._record.update(
            {
                Fields.EFFECTIVE_DATE.value: str(self.model_obj.eff_date),
                Fields.PRIVATE_LABEL.value: str(self),
                Fields.CATEGORY.value: self.model_obj.category(),
                Fields.RATINGS_AC_TXV.value: self.ratings_ac_txv,
                Fields.RATINGS_HP_TXV.value: self.ratings_hp_txv,
            }
        )
        return self._record
