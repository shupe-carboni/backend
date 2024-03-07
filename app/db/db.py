from dotenv import load_dotenv; load_dotenv()
import re
import os
from enum import StrEnum, auto
from typing import Iterable, Literal
from sqlalchemy import create_engine, text, URL, Result
from sqlalchemy.orm import Session, sessionmaker
from pandas import DataFrame, read_sql


class Stage(StrEnum):
    """used for separating product and pricing status by line item while
        keeping the history of proposals and active pricing used"""
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
    _ENGINE = create_engine(_connection_str)
    _SESSIONLOCAL = sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False)

    def __init__(self, database_name: str='') -> None:
        self.PREFIX = database_name + "_" if database_name else None

    def __str__(self) -> str:
        return f"<Database obj, connection_path: {self._connection_str}, subgroup: {self.PREFIX[:-1] if self.PREFIX else None}>"

    def get_db(self):
        session = self._SESSIONLOCAL()
        try:
            yield session
        finally:
            session.close()
    
    def full_table_name(self, table_name: str) -> str:
        return f"""{self.PREFIX}{table_name.replace('-', '_')}"""
    
    def upload_df(
            self,
            session: Session,
            data: DataFrame,
            table_name: str,
            primary_key: bool=True,
            if_exists: str='append'
        ) -> None:
        full_table_name = self.full_table_name(table_name)
        data.to_sql(full_table_name, con=session.get_bind(), if_exists=if_exists, index=False)
        if primary_key and if_exists == 'replace':
            sql = f"""
                    ALTER TABLE {full_table_name}
                    ADD COLUMN id SERIAL PRIMARY KEY;
            """
            session.execute(text(sql))

    def load_df(
            self,
            session: Session,
            table_name: str,
            customer_id: int=None,
            is_null: str=None,
        ) -> DataFrame:
        sql = f"""SELECT * FROM {self.full_table_name(table_name)}"""
        params = None
        if customer_id:
            sql += """ WHERE customer_id IN %(customer_id)s"""
            params = dict(customer_id=(customer_id,))
        elif is_null:
            sql += f""" WHERE {is_null} IS NULL"""
        sql += ";"
        return read_sql(sql, con=session.get_bind(), params=params)
    
    def execute(
            self,
            session: Session,
            sql: str,
            params: Iterable[dict|str|int|None]=None
        ) -> Result:
        ## add prefix to custom query table_name
        substitution = lambda match: match.group(0).replace(match.group(1), f'{self.PREFIX}{match.group(1)}')
        sql = re.sub(r'(?:FROM|UPDATE|INSERT INTO|TABLE)\s+([^\s,;]+)', substitution, sql, count=1)
        return session.execute(text(sql),params=params)
    
    def test(self, session: Session) -> str:
        with session.begin():
            return session.execute(text('SELECT version();')).fetchone()[0]
    
    def get_permitted_customer_location_ids(
            self,
            session: Session,
            email_address: str,
            select_type: Literal['customer_std','customer_manager','customer_admin']
        ) -> list[int]:
        """Using select statements, get the customer location ids that will be permitted for view
            select_type:
                * user - get only the customer location associated with the user. which ought to be 1 id
                * manager - get customer locations associated with all mapped branches in the sca_manager_map table
                * admin - get all customer locations associated with the customer id associated with the location associated to the user.:W
        """
        sql_user_only = """
            SELECT cl.id
            FROM sca_customer_locations cl
            WHERE EXISTS (
                SELECT 1
                FROM sca_users u
                WHERE u.email = :user_email
                AND u.customer_location_id = cl.id
            );
        """
        sql_manager = """
            SELECT cl.id
            FROM sca_customer_locations cl
            WHERE EXISTS (
                SELECT 1
                FROM sca_users u
                JOIN sca_manager_map mm
                ON mm.user_id = u.id
                WHERE u.email = :user_email
                AND mm.customer_location_id = cl.id
            );
        """
        sql_admin = """
            SELECT scl.id
            FROM sca_customer_locations scl
            WHERE EXISTS (
                SELECT 1
                FROM sca_users u
                JOIN sca_customer_locations customer_loc ON u.customer_location_id = customer_loc.id
                WHERE u.email = :user_email
                AND customer_loc.customer_id = scl.customer_id
            );
        """
        match select_type:
            case 'customer_std':
                sql = sql_user_only
            case 'customer_manager':
                sql = sql_manager
            case 'customer_admin':
                sql = sql_admin
            case _:
                raise Exception('invalid select_type')

        return session.scalars(text(sql), params={'user_email': email_address}).all()



ADP_DB = Database('adp')
SCA_DB = Database('sca')