from app.db import ADP_DB, Session

def load_pricing(session: Session):
    pricing = ADP_DB.load_df(session=session, table_name='pricing_hh_series')
    __adders_df = ADP_DB.load_df(session=session, table_name='price_adders')
    __adders_df = __adders_df.loc[__adders_df['series'] == 'HH', ['key', 'price']]
    adders = dict()
    for row in __adders_df.itertuples():
        adders[row.key] = row.price
    return pricing, adders