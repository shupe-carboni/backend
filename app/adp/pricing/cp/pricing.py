from app.db import Database

db = Database('adp')

pricing = db.load_df('pricing-cp-series')