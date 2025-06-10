import re
import pandas as pd
import openpyxl as opxl
import logging
from datetime import datetime
from typing import NamedTuple
from sqlalchemy.engine.cursor import CursorResult
from openpyxl.worksheet.worksheet import Worksheet
import warnings

warnings.simplefilter("ignore")
from app.db import DB_V2, Session
from app.adp.models import Ratings

logger = logging.getLogger("uvicorn.info")


class NotEnoughData(Exception):
    def __init__(self, file: str, sheet: str, *args: object) -> None:
        super().__init__(*args)
        self.file = file
        self.sheet = sheet


class Rating:
    expected_ahri_col_value = re.compile(
        r"^(\d*|pending|requested|upon request|)$", re.IGNORECASE
    )

    def __init__(self, **kwargs):
        self.ahri_number = kwargs.get("AHRINumber".lower())
        self.outdoor_model = kwargs.get("OutdoorModel".lower())
        self.oem_name = kwargs.get("OEMName".lower())
        self.indoor_model = kwargs.get("IndoorModel".lower())
        self.furnace_model = kwargs.get("FurnaceModel".lower())

    def __str__(self) -> str:
        return (
            f"AHRI: {self.ahri_number}, ODU: {self.outdoor_model}, "
            f"IDU: {self.indoor_model}, Furn: {self.furnace_model}"
        )

    @classmethod
    def is_valid_content(cls, ahri: str, outdoor: str, indoor: str) -> bool:
        result = False
        if not ahri and outdoor:
            ahri = ""
        try:
            result = bool(cls.expected_ahri_col_value.match(ahri))
        except TypeError as e:
            result = False
        return result

    def record(self) -> dict:
        return {
            "AHRINumber": self.ahri_number,
            "OutdoorModel": self.outdoor_model,
            "OEMName": self.oem_name,
            "IndoorModel": self.indoor_model,
            "FurnaceModel": self.furnace_model,
        }


def extract_ratings_from_file(file: str) -> set[Rating]:
    wb = opxl.load_workbook(file, data_only=True)
    ratings: list[Rating] = list()
    for sheet in wb.worksheets:
        ratings.extend(extract_ratings_from_sheet(sheet=sheet))
    return set(ratings)


def extract_ratings_from_sheet(sheet: Worksheet) -> list[Rating]:
    HEADERS = set(
        [
            name.lower()
            for name in (
                "AHRINumber",
                "OEMName",
                "OutdoorModel",
                "IndoorModel",
                "FurnaceModel",
            )
        ]
    )
    ratings = list()
    positions = dict()
    for row in sheet:
        column_values = [cell.value for cell in row]
        column_values_str = list()
        for val in column_values:
            if val:
                if val == "#N/A":
                    column_values_str.append(None)
                else:
                    column_values_str.append(str(val))
            else:
                column_values_str.append(None)
        if not positions:
            vals = [
                str(col).lower().strip().replace(" ", "") for col in column_values_str
            ]
            if intersect := set(vals) & HEADERS:
                if "ahrinumber" in intersect:
                    positions = {col: vals.index(col) for col in intersect}
        elif any(column_values_str):
            ahri = positions.get("AHRINumber".lower())
            ahri = column_values_str[ahri]  # inclusion of AHRINumber is guaranteed
            outdoor = positions.get("OutdoorModel".lower())
            outdoor = column_values_str[outdoor] if outdoor else None
            indoor = positions.get("IndoorModel".lower())
            indoor = column_values_str[indoor] if indoor else None
            if Rating.is_valid_content(ahri, outdoor, indoor):
                rating = Rating(
                    **{col: column_values_str[pos] for col, pos in positions.items()}
                )
                ratings.append(rating)
            else:
                continue

    return ratings


def find_ratings_in_reference(session: Session, ratings: pd.DataFrame) -> pd.DataFrame:
    """
    Notes:
        IS NOT DISTINCT FROM used for furnaces in `enrich_ratings`
        allows for 'NULL = NULL' to evaulate to True, instead of NULL.

        source: https://www.postgresql.org/docs/current/functions-comparison.html
        datatype IS NOT DISTINCT FROM datatype → boolean
            Equal, treating null as a comparable value.
            1 IS NOT DISTINCT FROM NULL → f (rather than NULL)
            NULL IS NOT DISTINCT FROM NULL → t (rather than NULL)
    """
    temp_table_name = "adp_temp_ratings"
    my_ratings = ratings
    try:
        my_ratings["AHRINumber"] = my_ratings["AHRINumber"].str.replace(
            "'", "", regex=False
        )
        my_ratings["AHRINumber"] = pd.to_numeric(
            my_ratings["AHRINumber"], errors="coerce"
        )
    except AttributeError:
        pass
    my_ratings["AHRINumber"] = my_ratings["AHRINumber"].fillna(0).astype(int)
    logger.info("creating temp ratings table")
    DB_V2.upload_df(
        session=session,
        data=my_ratings,
        table_name=temp_table_name,
        primary_key=False,
        if_exists="replace",
    )
    logger.info("table created")
    enrich_ratings = f"""
            SELECT *
            FROM {temp_table_name} as mr
            LEFT JOIN adp_all_ratings as r
            ON (mr."OutdoorModel" = r."Model Number"
                AND mr."IndoorModel" = r."Coil Model Number"
                AND mr."OEMName" = r."OEM Name"
                AND mr."FurnaceModel" IS NOT DISTINCT FROM r."Furnace Model Number")
            OR (mr."AHRINumber" = r."AHRI Ref Number");
            """
    logger.info("executing query for search")
    enriched_ratings: CursorResult = DB_V2.execute(session=session, sql=enrich_ratings)
    logger.info("query done")
    ratings_df = pd.DataFrame(enriched_ratings.mappings().fetchall())
    ratings_df["AHRI Ref Number"] = pd.to_numeric(
        ratings_df["AHRI Ref Number"], errors="coerce"
    )
    ratings_df["AHRI Ref Number"] = ratings_df["AHRI Ref Number"].fillna(0).astype(int)
    ratings_df["effective_date"] = str(datetime.today().date())
    return ratings_df


def find_ratings_in_reference_and_update_file(
    session: Session, ratings: pd.DataFrame
) -> None:
    temp_table_name = "adp_temp_ratings"
    with session.begin():
        try:
            ratings_df: pd.DataFrame = find_ratings_in_reference(
                session=session, ratings=ratings
            )
            DB_V2.upload_df(
                session=session,
                data=ratings_df,
                table_name="adp_program_ratings",
                primary_key=False,
                if_exists="append",
            )
            DB_V2.execute(session=session, sql=f"DROP TABLE {temp_table_name};")
        except Exception as e:
            logger.critical(e)
            raise e
    return


def update_all_unregistered_program_ratings(session: Session) -> None:
    program_ratings = DB_V2.load_df(session=session, table_name="adp_program_ratings")
    program_ratings["AHRI Ref Number"] = program_ratings["AHRI Ref Number"].astype(int)
    missing_ratings = program_ratings.loc[
        program_ratings["AHRI Ref Number"] == 0,
        ["AHRINumber", "OutdoorModel", "OEMName", "IndoorModel", "FurnaceModel", "id"],
    ]
    logger.info("Searching for ratings to update")
    result: pd.DataFrame = find_ratings_in_reference(
        session=session, ratings=missing_ratings
    )
    col_mask = ~result.columns.isin(missing_ratings.columns)
    selected_columns = result.columns[col_mask].tolist()
    selected_columns.extend(["id", "AHRINumber"])
    result = result.loc[result["AHRI Ref Number"] > 0, selected_columns]
    if result.empty:
        logger.info("No ratings to update")
        return
    result["AHRINumber"] = result["AHRI Ref Number"]
    result = pd.DataFrame.infer_objects(result)
    logger.info("Ratings found to update")
    tuple_names = ["Index"] + result.columns.to_list()
    logger.info(tuple_names)
    for record in result.itertuples():
        record: NamedTuple
        logging_msg = f"{record.AHRINumber}"
        logger.info(logging_msg)
        update_sets = "SET "
        for field, value in zip(tuple_names, record._asdict().values()):
            if field in ("Index", "id"):
                continue
            if not isinstance(value, str) and value is not None:
                update_sets += f""""{field}" = {value},"""
            elif field == "effective_date":
                update_sets += f""""{field}" = '{value}'::TIMESTAMP,"""
            elif value is None:
                update_sets += f""""{field}" = NULL,"""
            else:
                update_sets += f""""{field}" = '{value}',"""
        update_sets = update_sets[:-1]
        sql = f"""
            UPDATE adp_program_ratings
            {update_sets}
            WHERE id = :record_id
        """
        with session:
            DB_V2.execute(session=session, sql=sql, params={"record_id": record.id})
            session.commit()


def download_and_process_ratings_data():
    link = "https://www.adpinside.com/Compass/UserScreens/Monthly_spreadsheet_template.xlsm"
    try:
        logger.info("Downloading")
        with pd.ExcelFile(link) as file:
            logger.info("Finished download")
            ac = file.parse("ADP ARI Ratings AC", skiprows=5)
            hp = file.parse("ADP ARI Ratings HP", skiprows=5)
            ratings = pd.concat([ac, hp], ignore_index=True)
            ratings["Coil Model Number"] = ratings["Coil Model Number"].str.replace(
                r"\+TD$", "", regex=True
            )
            ratings["AHRI Ref Number"] = ratings["AHRI Ref Number"].astype(int)
    except Exception as e:
        logger.critical(f"Update Failed \n {e}")
    else:
        logger.info("Data Formatted")
        return ratings


def upload_ratings_data(session: Session, ratings: pd.DataFrame):
    try:
        with session.begin():
            logger.info("Replacing Database table")
            DB_V2.upload_df(
                session=session,
                data=ratings,
                table_name="adp_all_ratings",
                primary_key=False,
                if_exists="replace",
            )
            for ind_col in (
                "Model Number",
                "Coil Model Number",
                "OEM Name",
                "Furnace Model Number",
                "AHRI Ref Number",
            ):
                logger.info(f"Creating index for {ind_col}")
                DB_V2.execute(
                    session=session,
                    sql=f"""CREATE INDEX ON adp_all_ratings("{ind_col}");""",
                )
    except Exception as e:
        logger.critical(f"Update Failed \n {e}")
    else:
        logger.info("Update Complete")
    finally:
        session.close()


def update_ratings_reference(session: Session) -> None:
    ratings = download_and_process_ratings_data()
    upload_ratings_data(session, ratings)


def add_ratings_to_program(
    session: Session, adp_customer_id: int, ratings: Ratings
) -> None:
    ratings_df = pd.DataFrame(ratings.model_dump()["ratings"])
    ratings_df["customer_id"] = adp_customer_id
    cols_to_rn = ("SEER2", "EER95F2", "Capacity2", "HSPF2")
    ratings_df.rename(
        columns={col: col.lower() + "_as_submitted" for col in cols_to_rn}, inplace=True
    )
    find_ratings_in_reference_and_update_file(session=session, ratings=ratings_df)
