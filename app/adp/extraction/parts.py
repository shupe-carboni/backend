from app.db import ADP_DB
from pandas import DataFrame
session = next(ADP_DB.get_db())

def add_parts_to_program(adp_alias: str, part_nums: list[str]) -> None:
    customers = ADP_DB.load_df(session, 'customers')
    customer_id = customers.loc[customers['adp_alias'] == adp_alias,'id'].item() if adp_alias in customers['adp_alias'].values else None
    if not customer_id:
        raise Exception('customer not found')
    df = DataFrame(part_nums, columns=['part_number'])
    df.insert(0, 'customer_id', customer_id)
    ADP_DB.upload_df(session=session, data=df, table_name='program_parts', if_exists='append')
    