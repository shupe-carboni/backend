from app.db import ADP_DB, Session
from pandas import DataFrame

def add_parts_to_program(session: Session, adp_customer_id: int, part_nums: list[str]) -> None:
    df = DataFrame(part_nums, columns=['part_number'])
    df.insert(0, 'customer_id', adp_customer_id)
    with session.begin():
        ADP_DB.upload_df(
            session=session,
            data=df,
            table_name='program_parts',
            primary_key=False,
            if_exists='append')

    