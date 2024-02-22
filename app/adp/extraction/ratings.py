import re
import os
import pandas as pd
import openpyxl as opxl
from datetime import datetime
from typing import NamedTuple
from sqlalchemy.engine.cursor import CursorResult
from openpyxl.worksheet.worksheet import Worksheet
import warnings; warnings.simplefilter('ignore')
from app.db import ADP_DB, Session

session = next(ADP_DB.get_db())
TODAY = str(datetime.today().date())

class NotEnoughData(Exception):
    def __init__(self, file: str, sheet: str, *args: object) -> None:
        super().__init__(*args)
        self.file = file
        self.sheet = sheet

class Rating:
    expected_ahri_col_value = re.compile(r'^(\d*|pending|requested|upon request|)$', re.IGNORECASE)
    def __init__(self, **kwargs):
        self.ahri_number = kwargs.get('AHRINumber'.lower())
        self.outdoor_model = kwargs.get('OutdoorModel'.lower())
        self.oem_name = kwargs.get('OEMName'.lower())
        self.indoor_model = kwargs.get('IndoorModel'.lower())
        self.furnace_model = kwargs.get('FurnaceModel'.lower())

    def __str__(self) -> str:
        return f"AHRI: {self.ahri_number}, ODU: {self.outdoor_model}, IDU: {self.indoor_model}, Furn: {self.furnace_model}"

    @classmethod
    def is_valid_content(cls, ahri: str, outdoor: str, indoor: str) -> bool:
        result = False
        if not ahri and outdoor:
            ahri = ''
        try:
            result = bool(cls.expected_ahri_col_value.match(ahri))
        except TypeError as e:
            result = False
        return result

    def record(self) -> dict:
        return {
			'AHRINumber': self.ahri_number,
			'OutdoorModel': self.outdoor_model,
			'OEMName': self.oem_name,
			'IndoorModel': self.indoor_model,
            'FurnaceModel': self.furnace_model
        }


# def extract_ratings_all_ratings_from_dir(dir: str) -> tuple[pd.DataFrame, pd.DataFrame]:
#     data: dict[str, dict[str, set[Rating] | list[tuple[str, str]]]] = dict()
#     ## ratings extraction
#     for root, _, files in os.walk(dir):
#         for file in files:
#             program: str = os.path.basename(file).replace('.xlsx','')
#             program = re.sub(r'\d{4}-\d{1,2}-\d{1,2}', '', program).strip()
#             alias = PROGS_TO_ALIAS.loc[PROGS_TO_ALIAS['program'] == program,'adp_alias'].item()
#             customer = CUSTOMERS.loc[CUSTOMERS['adp_alias'] == alias, 'customer'].item()
#             if not data.get(customer):
#                 data[customer] = {'ratings': set()}
#                 data[customer]['errors'] = list()
#             results = extract_ratings_from_file(os.path.join(root,file))
#             data[customer]['ratings'] |= results
#     # formatting into a df and tagging the program
#     dfs = []
#     errors = []
#     for customer in data:
#         records = [record.record() for record in data[customer]['ratings']]
#         df = pd.DataFrame.from_records(data=records).dropna(how="all").drop_duplicates()
#         if df.isna().all().all():
#             pass
#         df['customer'] = customer
#         dfs.append(df)
#         errors.append(pd.DataFrame(data[customer]['errors'], columns=['File', 'Sheet']))
#     result = pd.concat(dfs)
#     result = result.loc[~result['AHRINumber'].astype(str).str.contains("AHRINumber"), :]
#     errors = pd.concat(errors)
#     return result, errors

def extract_ratings_from_file(file: str) -> set[Rating]:
    wb = opxl.load_workbook(file, data_only=True)
    ratings: list[Rating] = list()
    for sheet in wb.worksheets:
        ratings.extend(extract_ratings_from_sheet(sheet=sheet))
    return set(ratings)
    
def extract_ratings_from_sheet(sheet: Worksheet) -> list[Rating]:
    HEADERS = set([name.lower() for name in ('AHRINumber', 'OEMName', 'OutdoorModel','IndoorModel','FurnaceModel')])
    ratings = list()
    positions = dict()
    for row in sheet:
        column_values = [cell.value for cell in row]
        column_values_str = list()
        for val in column_values:
            if val:
                if val == '#N/A':
                    column_values_str.append(None)
                else:
                    column_values_str.append(str(val))
            else:
                column_values_str.append(None)
        if not positions:
            vals = [str(col).lower().strip().replace(' ', '') for col in column_values_str]
            if intersect := set(vals) & HEADERS:
                if 'ahrinumber' in intersect:
                    positions = {col: vals.index(col) for col in intersect}
        elif any(column_values_str):
            ahri = positions.get('AHRINumber'.lower())
            ahri = column_values_str[ahri] # inclusion of AHRINumber is guaranteed
            outdoor = positions.get('OutdoorModel'.lower())
            outdoor = column_values_str[outdoor] if outdoor else None
            indoor = positions.get('IndoorModel'.lower())
            indoor = column_values_str[indoor] if indoor else None
            if Rating.is_valid_content(ahri, outdoor, indoor):
                rating = Rating(**{col: column_values_str[pos] for col, pos in positions.items()})
                ratings.append(rating)
            else:
                continue
                print(ahri, outdoor, indoor)

    return ratings

def find_ratings_in_reference(session: Session, ratings: pd.DataFrame) -> pd.DataFrame:
    temp_table_name = 'temp_ratings'
    my_ratings = ratings
    try:
        my_ratings['AHRINumber'] = my_ratings['AHRINumber'].str.replace("'","", regex=False)
        my_ratings['AHRINumber'] = pd.to_numeric(my_ratings['AHRINumber'], errors='coerce')
    except AttributeError:
        pass
    my_ratings['AHRINumber'] = my_ratings['AHRINumber'].fillna(0).astype(int)
    with session.begin():
        ADP_DB.upload_df(session=session, data=my_ratings, table_name=temp_table_name, primary_key=False)
    """
    IS NOT DISTINCT FROM used for furnaces allows for 'NULL = NULL' to evaulate to True, instead of NULL.
        source: https://www.postgresql.org/docs/current/functions-comparison.html
        datatype IS NOT DISTINCT FROM datatype → boolean
            Equal, treating null as a comparable value.
            1 IS NOT DISTINCT FROM NULL → f (rather than NULL)
            NULL IS NOT DISTINCT FROM NULL → t (rather than NULL)
    """
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
    enriched_ratings: CursorResult = ADP_DB.execute_and_commit(session=session, table_name=enrich_ratings)
    ratings_df = pd.DataFrame(enriched_ratings.mappings().fetchall())
    ratings_df['AHRI Ref Number'] = pd.to_numeric(ratings_df['AHRI Ref Number'], errors='coerce')
    ratings_df['AHRI Ref Number'] = ratings_df['AHRI Ref Number'].fillna(0).astype(int)
    ratings_df['Effective Date'] = TODAY
    return ratings_df

def find_ratings_in_reference_and_update_file(session: Session, ratings: pd.DataFrame) -> None:
    temp_table_name = 'temp_ratings'
    ratings_df = find_ratings_in_reference(ratings=ratings)
    with session.begin():
        ADP_DB.upload_df(session=session, data=ratings_df, table_name='program_ratings', primary_key=False, if_exists='append')
        ADP_DB.execute(session=session, sql=f"DROP TABLE {temp_table_name};")
    return

def update_all_unregistered_program_ratings(session: Session) -> None:
    program_ratings = ADP_DB.load_df(session=session, table_name='program_ratings')
    program_ratings['AHRI Ref Number'] = program_ratings['AHRI Ref Number'].astype(int)
    missing_ratings = program_ratings[program_ratings['AHRI Ref Number'] == 0].iloc[:,list(range(6))+[-1]]
    result = find_ratings_in_reference(ratings=missing_ratings)
    col_mask = ~result.columns.isin(missing_ratings.columns)
    selected_columns = result.columns[col_mask].tolist()
    selected_columns.extend(['id', 'AHRINumber'])
    result = result.loc[result['AHRI Ref Number'] > 0, selected_columns]
    result['AHRINumber'] = result['AHRI Ref Number']
    result = pd.DataFrame.infer_objects(result)
    print("updating these ratings")
    tuple_names = ['Index']+result.columns.to_list()
    for record in result.itertuples():
        record: NamedTuple
        print('\t',record)
        update_sets = "SET "
        for field, value in zip(tuple_names,record._asdict().values()):
            if field in ('Index', 'id'):
                continue
            if not isinstance(value, str) and value is not None:
                update_sets += f""""{field}" = {value},"""
            elif field == 'Effective Date':
                update_sets += f""""{field}" = '{value}'::TIMESTAMP,"""
            elif value is None:
                update_sets += f""""{field}" = NULL,"""
            else:
                update_sets += f""""{field}" = '{value}',"""
        update_sets = update_sets[:-1]
        sql = f"""
            UPDATE program_ratings
            {update_sets}
            WHERE id = :record_id
        """
        # commit happens up-stack
        ADP_DB.execute(session=session, sql=sql, params={"record_id": record.id})

def update_ratings_reference(session: Session):
    global process_complete
    process_complete = False
    link = 'https://www.adpinside.com/Compass/UserScreens/Monthly_spreadsheet_template.xlsm'
    try:
        print('Downloading')
        with pd.ExcelFile(link) as file:
            print('Finished download')
            ac = file.parse('ADP ARI Ratings AC', skiprows=5)
            hp = file.parse('ADP ARI Ratings HP', skiprows=5)
            ratings = pd.concat([ac, hp], ignore_index=True)
            ratings['Coil Model Number'] = ratings['Coil Model Number'].str.replace(r'\+TD$','', regex=True)
            ratings['AHRI Ref Number'] = ratings['AHRI Ref Number'].astype(int)
            print('Replacing Database table')
            with session.begin():
                ADP_DB.upload_df(session=session, data=ratings, table_name='all_ratings', primary_key=False)
    except Exception as e:
        print('Update Failed')
        print(e)
    finally:
        process_complete = True
        print("Update Complete")

def add_rating_to_program(session: Session, adp_alias: str, rating: dict[str,str]) -> None:
    CUSTOMERS = ADP_DB.load_df(session=session, table_name='customers')
    sca_customer_name = CUSTOMERS.loc[CUSTOMERS['adp_alias'] == adp_alias, 'customer']
    rating |= {'customer': sca_customer_name}
    rating_df = pd.DataFrame(rating)
    find_ratings_in_reference_and_update_file(session=session, ratings=rating_df)