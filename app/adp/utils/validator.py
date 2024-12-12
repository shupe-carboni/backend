import re
from logging import getLogger
from app.db import Session, ADP_DB, ADP_DB_2024
from app.adp.adp_models.model_series import ModelSeries, NoBasePrice
from app.adp.utils.models import ParsingModes

logger = getLogger("uvicorn.info")


class Validator:
    def __init__(
        self, db_session: Session, raw_text: str, model_series: ModelSeries
    ) -> None:
        self.raw_text = (
            (str(raw_text).strip().upper().replace(" ", "").replace("-", ""))
            if raw_text
            else None
        )
        self.text_len = len(self.raw_text) if self.raw_text else 0
        self.model_series = model_series
        self.session = db_session

    def is_model(
        self, price_strat: ParsingModes = ParsingModes.BASE_PRICE
    ) -> ModelSeries | bool:
        if self.text_len not in self.model_series.text_len or not self.raw_text:
            return False
        price_strat_map = {
            ParsingModes.BASE_PRICE: ADP_DB,
            ParsingModes.BASE_PRICE_2024: ADP_DB_2024,
        }
        model = re.compile(self.model_series.regex, re.VERBOSE)
        model_parsed = model.match(self.raw_text)
        if model_parsed:
            try:
                return self.model_series(
                    session=self.session,
                    re_match=model_parsed,
                    db=price_strat_map[price_strat],
                )
            except NoBasePrice as np:
                logger.error(
                    f"Model {model_parsed.group(0)} unable to be produced due to an error: {np.reason}"
                )
                return False
            except Exception as e:
                e_type = e.__class__.__name__
                e_val = str(e)
                logger.critical(f"{e_type}: {e_val}")
                return False
        else:
            return False
