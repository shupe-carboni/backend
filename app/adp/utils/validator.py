import re
from app.db import Session
from app.adp.adp_models.model_series import ModelSeries

class Validator:
    def __init__(self, db_session: Session, raw_text: str, model_series: ModelSeries) -> None:
        self.raw_text = (
            str(raw_text)
                .strip()
                .upper()
                .replace(' ','')
                .replace('-','')
        ) if raw_text else None
        self.text_len = len(self.raw_text) if self.raw_text else 0
        self.model_series = model_series
        self.session = db_session
    
    def is_model(self) -> ModelSeries|bool:
        if self.text_len not in self.model_series.text_len or not self.raw_text:
            return False
        model = re.compile(self.model_series.regex, re.VERBOSE)
        model_parsed = model.match(self.raw_text)
        if model_parsed:
            return self.model_series(db_session=self.session, re_match=model_parsed)
        else:
            return False