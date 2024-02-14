from db.db import Database

db = Database('adp')
pricing = db.load_df('pricing-sc-series')