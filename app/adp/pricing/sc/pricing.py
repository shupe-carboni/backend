from app.db import ADP_DB, Session

def load_pricing(session: Session):
    pricing = ADP_DB.load_df(session=session, table_name='pricing-sc-series')
    return pricing