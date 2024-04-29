from dotenv import load_dotenv; load_dotenv()
import re
import os
import boto3
import botocore
from dataclasses import dataclass
from io import BytesIO
from enum import StrEnum, auto
from typing import Iterable, Literal
from sqlalchemy import create_engine, text, URL, Result
from sqlalchemy.orm import Session, sessionmaker
from pandas import DataFrame, read_sql

@dataclass
class File:
    file_name: str
    file_mime: str
    file_content: bytes|BytesIO

class Stage(StrEnum):
    """used for separating product and pricing status by line item while
        keeping the history of proposals and active pricing used"""
    PROPOSED = auto()
    ACTIVE = auto()
    REJECTED = auto()
    REMOVED = auto()

class UserTypes(StrEnum):
    sca_admin = auto()
    sca_employee = auto()
    customer_admin = auto()
    customer_manager = auto()
    customer_std = auto()
    view_only = auto()

class S3:
    bucket = os.getenv('S3_BUCKET')
    client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
    )
    @classmethod
    def upload_file(cls, file: File, destination: str) -> None:
        try:
            cls.client.put_object(
                Body=file.file_content,
                Bucket=cls.bucket,
                Key= destination,
                ContentType=file.file_mime
            )
        except Exception as e:
            raise Exception(f'upload failed: {e}')

    @classmethod
    def get_file(cls ,key: str) -> File:
        response: dict = cls.client.get_object(Bucket=cls.bucket, Key=key)
        if response.get('HTTPStatusCode') == 200:
            file_data = response.get('Body').read()
            file_content_type: str = response.get('ContentType')
            file = File(os.path.basename(key),
                        file_mime=file_content_type, file_content=file_data)
            return file
        raise Exception('File Not Found')


class Database:

    conn_params = {
        'database': os.environ.get('RDS_DB_NAME'),
        'host': os.environ.get('RDS_HOSTNAME'),
        'password': os.environ.get('RDS_PASSWORD'),
        'port': os.environ.get('RDS_PORT'),
        'username': os.environ.get('RDS_USER')
    }

    _connection_url = URL.create('postgresql',**conn_params)
    # without doing this, the password is not properly passed
    # due to url encoding when passing the URL object
    _connection_str = _connection_url.render_as_string(hide_password=False)
    _ENGINE = create_engine(_connection_str)
    _SESSIONLOCAL = sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False)

    def __init__(self, database_name: str='') -> None:
        self.PREFIX = database_name + "_" if database_name else None

    def __str__(self) -> str:
        return f"<Database obj, connection_path: {self._connection_str}, "\
                "subgroup: {self.PREFIX[:-1] if self.PREFIX else None}>"

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
            id_only: bool=False
        ) -> DataFrame:
        if id_only:
            select = 'id'
        else:
            select = '*'
        sql = f"""SELECT {select} FROM {self.full_table_name(table_name)}"""
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
        user_type = UserTypes[select_type]
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
        query_set = {sql_admin, sql_manager, sql_user_only}
        match user_type:
            case UserTypes.customer_std:
                query_set.remove(sql_admin)
                query_set.remove(sql_manager)
            case UserTypes.customer_manager:
                query_set.remove(sql_admin)
            case UserTypes.customer_admin:
                pass
            case _:
                raise Exception('invalid select_type')
        
        for sql in query_set:
            result = session.scalars(text(sql), params={'user_email': email_address}).all() 
            if result:
                return result
        return []


ADP_DB = Database('adp')
SCA_DB = Database('sca')