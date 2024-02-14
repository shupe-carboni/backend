from db.db import Database

db = Database('adp')

pricing = db.load_df('pricing_he_series')
__adders_df = db.load_df('price_adders')
__adders_df = __adders_df.loc[__adders_df['series'] == 'HE', ['key', 'price']]
adders = dict()
for row in __adders_df.itertuples():
    adders[row.key] = row.price