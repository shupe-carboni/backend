import re
from logging import getLogger
from app.db import Session, DB_V2
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
        self,
        price_strat: ParsingModes = ParsingModes.BASE_PRICE,
        customer_id: int = 0,
    ) -> ModelSeries | bool:
        if self.text_len not in self.model_series.text_len or not self.raw_text:
            return False
        model = re.compile(self.model_series.regex, re.VERBOSE)
        model_parsed = model.match(self.raw_text)
        if model_parsed:
            try:
                match price_strat:
                    case ParsingModes.BASE_PRICE_FUTURE:
                        return self.model_series(
                            session=self.session,
                            re_match=model_parsed,
                            db=DB_V2,
                            use_future=True,
                            customer_id=0,
                        )
                    case ParsingModes.CUSTOMER_PRICING_FUTURE:
                        return self.model_series(
                            session=self.session,
                            re_match=model_parsed,
                            db=DB_V2,
                            use_future=True,
                            customer_id=customer_id,
                        )
                    case ParsingModes.BASE_PRICE:
                        return self.model_series(
                            session=self.session,
                            re_match=model_parsed,
                            db=DB_V2,
                            use_future=False,
                            customer_id=0,
                        )
                    case ParsingModes.CUSTOMER_PRICING:
                        return self.model_series(
                            session=self.session,
                            re_match=model_parsed,
                            db=DB_V2,
                            use_future=False,
                            customer_id=customer_id,
                        )
            except NoBasePrice as np:
                logger.error(
                    f"Model {model_parsed.group(0)} unable to be "
                    f"produced due to an error: {np.reason}"
                )
                return False
            except Exception as e:
                e_type = e.__class__.__name__
                e_val = str(e)
                logger.critical(f"{e_type}: {e_val}")
                import traceback as tb

                logger.info(tb.format_exc())
                return False
        else:
            return False
