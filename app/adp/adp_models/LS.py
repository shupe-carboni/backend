import re
from app.adp.adp_models.model_series import ModelSeries
from app.db import Session, Database


class LS(ModelSeries):
    text_len = (13, 14)
    regex = r"""
        (?P<paint>L)
        (?P<motor>[S|E])
        (?P<config>M)
        (?P<ton>\d{2})
        (?P<meter>[\d|A|B])
        (?P<scode>\d{2}\D|\d\D{2})
        (?P<line_conn>[S|B])
        (?P<heat>\d{2})
        (?P<voltage>\d)
        (?P<rds>R)
        """

    def __init__(self, session: Session, re_match: re.Match, db: Database):
        super().__init__(session, re_match, db)
