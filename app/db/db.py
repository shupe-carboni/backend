from dotenv import load_dotenv

load_dotenv()
import re
import os
import boto3
import asyncio
from logging import getLogger
from dataclasses import dataclass
from io import BytesIO
from enum import StrEnum, auto
from typing import Iterable
from fastapi import HTTPException
from sqlalchemy import create_engine, text, URL, Result
from sqlalchemy.orm import Session, sessionmaker
from pandas import DataFrame, read_sql

logger = getLogger("uvicorn.info")
TEST_DB = os.getenv("TEST_DATABASE")


@dataclass
class File:
    file_name: str
    file_mime: str
    file_content: bytes | BytesIO


class Stage(StrEnum):
    """used for separating product and pricing status by line item while
    keeping the history of proposals and active pricing used"""

    PROPOSED = auto()
    ACTIVE = auto()
    REJECTED = auto()
    REMOVED = auto()


class UserTypes(StrEnum):
    developer = auto()
    sca_admin = auto()
    sca_employee = auto()
    customer_admin = auto()
    customer_manager = auto()
    customer_std = auto()
    view_only = auto()


class FriedrichPriceLevels(StrEnum):

    NON_STOCKING = auto()
    STOCKING = auto()
    STANDARD = auto()


class FriedrichMarketType(StrEnum):

    HOTEL_LODGING = auto()
    MULTI_FAMILY = auto()
    HOSPITAL_ASSISTED_LIVING = auto()
    SCHOOL = auto()
    GOVERNMENT = auto()


class S3:
    bucket = os.getenv("S3_BUCKET")
    client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    )

    @classmethod
    def _sync_upload_file(cls, file: File, destination: str) -> None:
        try:
            cls.client.put_object(
                Body=file.file_content,
                Bucket=cls.bucket,
                Key=destination,
                ContentType=file.file_mime,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"upload failed: {e}")

    @classmethod
    async def upload_file(cls, file: File, destination: str) -> None:
        return await asyncio.to_thread(cls._sync_upload_file, file, destination)

    @classmethod
    def get_file(cls, key: str) -> File:
        try:
            response: dict = cls.client.get_object(Bucket=cls.bucket, Key=key)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"File Not Found: {e}")
        else:
            status_code: int = response["ResponseMetadata"]["HTTPStatusCode"]
            if status_code == 200:
                file_data = response.get("Body").read()
                file_content_type: str = response.get("ContentType")
                file = File(
                    os.path.basename(key),
                    file_mime=file_content_type,
                    file_content=BytesIO(file_data),
                )
                return file
            else:
                raise HTTPException(
                    status_code=404, detail=f"File Not Found: {response}"
                )


class Database:

    conn_params = (
        {
            "database": os.environ.get("RDS_DB_NAME"),
            "host": os.environ.get("RDS_HOSTNAME"),
            "password": os.environ.get("RDS_PASSWORD"),
            "port": os.environ.get("RDS_PORT"),
            "username": os.environ.get("RDS_USER"),
        }
        if not TEST_DB
        else None
    )

    _connection_url = URL.create("postgresql", **conn_params) if conn_params else None
    # without doing this, the password is not properly passed
    # due to url encoding when passing the URL object
    _connection_str = (
        _connection_url.render_as_string(hide_password=False)
        if _connection_url
        else TEST_DB
    )
    _ENGINE = create_engine(_connection_str)
    _SESSIONLOCAL = sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False)

    def __init__(self, database_name: str = "") -> None:
        self.PREFIX = database_name + "_" if database_name else None
        if TEST_DB:
            logger.info("Database: local")
        else:
            logger.info("Database: production")

    def __str__(self) -> str:
        if TEST_DB:
            return (
                f"<Database obj, connection_path: {self._connection_str}, "
                f"subgroup: {self.PREFIX[:-1] if self.PREFIX else None}>"
            )
        else:
            return (
                f"<Database obj, connection_path: {self._connection_url.render_as_string()}, "
                f"subgroup: {self.PREFIX[:-1] if self.PREFIX else None}>"
            )

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
        primary_key: bool = True,
        if_exists: str = "append",
    ) -> None:
        full_table_name = self.full_table_name(table_name)
        data.to_sql(
            full_table_name, con=session.get_bind(), if_exists=if_exists, index=False
        )
        if primary_key and if_exists == "replace":
            sql = f"""
                    ALTER TABLE {full_table_name}
                    ADD COLUMN id SERIAL PRIMARY KEY;
            """
            session.execute(text(sql))

    def load_df(
        self,
        session: Session,
        table_name: str,
        customer_id: int = None,
        is_null: str = None,
        id_only: bool = False,
    ) -> DataFrame:
        if id_only:
            select = "id"
        else:
            select = "*"
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
        params: Iterable[dict | str | int | None] = None,
    ) -> Result:
        ## add prefix to custom query table_name
        substitution = lambda match: match.group(0).replace(
            match.group(1), f"{self.PREFIX}{match.group(1)}"
        )
        sql = re.sub(
            r"(?:FROM|UPDATE|INSERT INTO|TABLE)\s+([^\s,;]+)",
            substitution,
            sql,
            count=1,
        )
        return session.execute(text(sql), params=params)

    def test(self, session: Session) -> str:
        with session.begin():
            return session.execute(text("SELECT version();")).fetchone()[0]


class DatabaseV2(Database):
    """Just use the given table names, no obfuscation of prefixs and hot-swapping
    the table name."""

    def full_table_name(self, table_name: str) -> str:
        return table_name

    def execute(
        self,
        session: Session,
        sql: str,
        params: Iterable[dict | str | int | None] = None,
    ) -> Result:
        return session.execute(text(sql), params=params)


ADP_DB = Database("adp")
ADP_DB_2024 = Database("_2024_adp")
SCA_DB = Database("sca")
DB_V2 = DatabaseV2()
