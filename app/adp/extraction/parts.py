from db.db import Database
from pandas import DataFrame
DATABASE = Database('adp')

def add_parts_to_program(adp_alias: str, part_nums: list[str]) -> None:
    customers = DATABASE.load_df('customers')
    customer_id = customers.loc[customers['adp_alias'] == adp_alias,'id'].item() if adp_alias in customers['adp_alias'].values else None
    if not customer_id:
        raise Exception('customer not found')
    df = DataFrame(part_nums, columns=['part_number'])
    df.insert(0, 'customer_id', customer_id)
    DATABASE.upload_df(data=df, table_name='program_parts', if_exists='append')
    