from app.db import ADP_DB

session = next(ADP_DB.get_db())

pricing = ADP_DB.load_df(session=session, table_name='pricing-cp-series')