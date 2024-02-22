
from app.db import ADP_DB

session = next(ADP_DB.get_db())

pricing = ADP_DB.load_df(session=session, table_name='pricing-s-series')
__adders_df = ADP_DB.load_df(session=session, table_name='price_adders')
__adders_df = __adders_df.loc[__adders_df['series'] == 'S', ['key', 'price']]
adders = dict()
for row in __adders_df.itertuples():
    adders[row.key] = row.price