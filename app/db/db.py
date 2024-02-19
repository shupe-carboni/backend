from dotenv import load_dotenv; load_dotenv()
import re
import os
from enum import StrEnum, auto
from typing import Iterable, Any
from sqlalchemy import create_engine, text, URL
from pandas import DataFrame, read_sql

class Status(StrEnum):
    PROPOSED = auto()
    ACTIVE = auto()
    REJECTED = auto()
    REMOVED = auto()


class Database:

    conn_params = {
        'database': os.environ.get('RDS_DB_NAME'),
        'host': os.environ.get('RDS_HOSTNAME'),
        'password': os.environ.get('RDS_PASSWORD'),
        'port': os.environ.get('RDS_PORT'),
        'username': os.environ.get('RDS_USER')
    }

    _connection_url = URL.create('postgresql',**conn_params)
    # without doing this, the password is not properly passed due to url encoding
    # when passing the URL object
    _connection_str = _connection_url.render_as_string(hide_password=False)
    ENGINE = create_engine(_connection_str)

    def __init__(self, database_name: str='') -> None:
        self.PREFIX = database_name + "_" if database_name else None
    
    def __str__(self) -> str:
        return f"<Database obj, connection_path: {self._connection_str}, subgroup: {self.PREFIX[:-1]}>"
    
    def full_table_name(self, table_name: str) -> str:
        return f"""{self.PREFIX}{table_name.replace('-', '_')}"""
    
    def upload_df(self, data: DataFrame, table_name: str, primary_key: bool=True, if_exists: str='replace') -> None:
        full_table_name = self.full_table_name(table_name)
        data.to_sql(full_table_name, con=self.ENGINE, if_exists=if_exists, index=False)
        if primary_key and if_exists == 'replace':
            with self.ENGINE.connect() as conn:
                with conn as cur:
                    try:
                        sql = f"""
                                ALTER TABLE {full_table_name}
                                ADD COLUMN id SERIAL PRIMARY KEY;
                        """
                        cur.execute(text(sql))
                    except Exception as e:
                        print(e)
                        conn.rollback()
                    else:
                        conn.commit()
                    finally:
                        conn.close()

    def load_df(self, table_name: str, customers: list[str]=None, is_null: str=None, use_alias: bool=False) -> DataFrame:
        sql = f"""SELECT * FROM {self.full_table_name(table_name)}"""
        params = None
        if customers:
            if use_alias:
                sql += """ WHERE adp_alias IN %(customers)s"""
            else:
                sql += """ WHERE "Customer" IN %(customers)s"""
            params = dict(customers=tuple(customers))
        elif is_null:
            sql += f""" WHERE {is_null} IS NULL"""
        sql += ";"
        return read_sql(sql, con=self.ENGINE, params=params)
    
    def execute_and_commit(self, sql: str, params: Iterable[str|int|None]=None) -> Any:
        ## add prefix to custom query table_name
        substitution = lambda match: match.group(0).replace(match.group(1), f'{self.PREFIX}{match.group(1)}')
        sql = re.sub(r'(?:FROM|UPDATE|INSERT INTO|TABLE)\s+([^\s,;]+)', substitution, sql, count=1)
        with self.ENGINE.connect() as conn:
            try:
                result = conn.execute(text(sql),parameters=params)
            except:
                import traceback as tb
                print(tb.format_exc())
                conn.rollback()
                return None
            else:
                conn.commit()
        return result
    
    def test(self) -> str:
        with self.ENGINE.connect() as conn:
            with conn as cur:
                result = cur.execute(text('SELECT version();'))
                return result.fetchone()[0]


