from app.db import ADP_DB, Session
from pandas import DataFrame

def load_pricing(session: Session) -> DataFrame:
    return ADP_DB.load_df(session=session, table_name='pricing-cp-series')