from dotenv import load_dotenv; load_dotenv()
import os
import pandas as pd
from dataclasses import dataclass
from typing import Iterable, Literal
from datetime import datetime
from openpyxl.styles import Font, Alignment, numbers
from app.adp.adp_models import Fields
from app.adp.programs import CoilProgram, AirHandlerProgram, CustomerProgram
from app.adp.utils.pricebook import PriceBook
from app.db import Database


TODAY = str(datetime.today().date())
SAVE_DIR = os.getenv('SAVE_DIR')
TEMPLATES = os.getenv('TEMPLATES')
LOGOS_DIR = os.getenv('LOGOS_DIR')
db = Database('adp')

@dataclass
class ProgramFile:
    file_name: str
    file_data: bytes


def build_coil_program(program_data: pd.DataFrame, ratings: pd.DataFrame) -> CoilProgram:
    program_data = program_data.drop(columns=['customer_id'])
    program_data = program_data.sort_values(by=[
        Fields.CATEGORY.value,
        Fields.SERIES.value,
        Fields.MPG.value,
        Fields.METERING.value,
        Fields.TONNAGE.value,
        Fields.WIDTH.value,
        Fields.HEIGHT.value
    ]).drop_duplicates()
    prog_ratings = ratings.drop(columns=[Fields.CUSTOMER_ID.value])
    return CoilProgram(program_data=program_data, ratings=prog_ratings)
    
def build_ah_program(program_data: pd.DataFrame, ratings: pd.DataFrame) -> AirHandlerProgram:
    program_data = program_data.drop(columns=['customer_id'])
    temp_heat_num_col = 'heat_num'
    program_data[temp_heat_num_col] = program_data[Fields.HEAT.value].str.extract(r'(\d+|\d\.\d)\s*kW').fillna(0).astype(float).astype(int)
    program_data = program_data.sort_values(by=[
        Fields.CATEGORY.value,
        Fields.SERIES.value,
        Fields.MPG.value,
        Fields.TONNAGE.value,
        Fields.WIDTH.value,
        temp_heat_num_col
    ]).drop_duplicates()
    program_data = program_data.drop(columns=[temp_heat_num_col])
    prog_ratings = ratings.drop(columns=[Fields.CUSTOMER_ID.value])
    return AirHandlerProgram(program_data=program_data, ratings=prog_ratings)

def add_customer_terms_parts_and_logo_path(customer_id: int, coil_prog: CoilProgram, ah_prog: AirHandlerProgram) -> CustomerProgram:
    footer = db.load_df("customer_terms_by_customer_id", customer_id=customer_id)
    prog_parts = db.load_df('program_parts_expanded', customer_id=customer_id)
    alias_mapping = db.load_df('customers')
    alias_mapping = alias_mapping[alias_mapping['id'] == customer_id]
    alias_name = alias_mapping[Fields.ADP_ALIAS.value].item()
    ## parts
    customer_parts = prog_parts.drop(columns='customer_id')
    customer_preferred = alias_mapping['preferred_parts'].item() == True
    ## specific column name for pricing is to be set
    if customer_preferred:
        part_price_col = 'preferred'
        # some "preferred" pricing is left blank, so default the price to standard pricing
        customer_parts[part_price_col] = customer_parts[part_price_col].fillna(customer_parts['standard'])
    else:
        part_price_col = 'standard'
    customer_parts = customer_parts[['part_number', 'description', 'pkg_qty', part_price_col]]
    ## footer
    try:
        payment_terms = footer['terms'].item()
        pre_paid_freight = footer['ppf'].item()
        effective_date = str(footer['effective_date'].item())
    except:
        print("footer capture failed")
        print(alias_name)
    terms = {
        'Payment Terms': {
            'value': payment_terms,
            'style': {
                'font': Font(bold=True),
                'alignment': Alignment(horizontal='right')
            }
        },
        'Freight': {
            'value': pre_paid_freight,
            'style': {
                'number_format': numbers.FORMAT_CURRENCY_USD,
                'font': Font(bold=True),
                'alignment': Alignment(horizontal='right')
            }
        },
        'Effective Date': {
            'value': datetime.strptime(effective_date, r'%Y-%m-%d %H:%M:%S'),
            'style': {
                'font': Font(bold=True),
                'alignment': Alignment(horizontal='right'),
                'number_format': numbers.FORMAT_DATE_YYYYMMDD2

            }
        }
    }
    ## logo_path
    logo_path = alias_mapping['logo_path'].item()
    full_logo_path = os.path.join(LOGOS_DIR, logo_path)
    return CustomerProgram(
            customer_id=customer_id,
            customer_name=alias_name,
            coils=coil_prog,
            air_handlers=ah_prog,
            parts=customer_parts,
            terms=terms,
            logo_path=full_logo_path
        )

def generate_program(
        customer_id: int,
        stage: Literal['ACTIVE', 'PROPOSED', 'REJECTED', 'REMOVED']='ACTIVE'
    ) -> ProgramFile:
    tables = ["coil_programs", "ah_programs", "program_ratings"]
    coil_prog_table, ah_prog_table, ratings = [db.load_df(table_name=table, customer_id=customer_id) for table in tables]
    coil_prog_table = coil_prog_table[coil_prog_table['stage'] == stage.upper()]
    ah_prog_table = ah_prog_table[ah_prog_table['stage'] == stage.upper()]
    try:
        coil_prog = build_coil_program(coil_prog_table, ratings)
        ah_prog = build_ah_program(ah_prog_table, ratings)
        full_program = add_customer_terms_parts_and_logo_path(
            customer_id=customer_id,
            coil_prog=coil_prog,
            ah_prog=ah_prog
        )
        print(f"generating {full_program}")
        for prog in full_program:
            print(f'\t{prog}')
        price_book = (PriceBook(TEMPLATES, full_program, save_path=SAVE_DIR)
                            .build_program()
                            .attach_nomenclature_tab()
                            .attach_ratings()
                            .attach_parts()
                            .save_and_close())
        new_program_file = ProgramFile(
            file_data=price_book,
            file_name=full_program.new_file_name()
        )
    except Exception:
        import traceback as tb
        print("Error occurred while trying to generate programs")
        print(tb.format_exc())
    else:
        tables.remove('program_ratings')
        update_dates_in_tables(db=db, tables=tables, customer_id=customer_id)
        return new_program_file

def update_dates_in_tables(
        db: Database,
        tables: Iterable[str],
        customer_id: int=None
    ) -> None:
    coil_update_q, ah_update_q = [f"""UPDATE {table} SET last_file_gen = :date WHERE customer_id IN :customers;""" for table in tables]
    params = {"customers": (customer_id,), "date": TODAY}
    for q in coil_update_q, ah_update_q:
        db.execute_and_commit(q, params)