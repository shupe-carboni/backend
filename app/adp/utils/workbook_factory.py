from dotenv import load_dotenv; load_dotenv()
import os
import pandas as pd
import logging
from dataclasses import dataclass
from typing import Iterable, Literal
from datetime import datetime
from openpyxl.styles import Font, Alignment, numbers
from app.adp.adp_models import Fields
from app.adp.utils.programs import CoilProgram, AirHandlerProgram, CustomerProgram, EmptyProgram
from app.adp.utils.pricebook import PriceBook
from app.db import Session, ADP_DB, SCA_DB, Stage


logger = logging.getLogger('uvicorn.info')
TODAY = str(datetime.today().date())
TEMPLATES = os.getenv('TEMPLATES')
LOGOS_DIR = os.getenv('LOGOS_DIR')

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

def add_customer_terms_parts_and_logo_path(session: Session, customer_id: int, coil_prog: CoilProgram, ah_prog: AirHandlerProgram) -> CustomerProgram:
    footer = ADP_DB.load_df(session=session, table_name="customer_terms_by_customer_id", customer_id=customer_id)
    prog_parts = ADP_DB.load_df(session=session, table_name='program_parts_expanded', customer_id=customer_id)
    alias_mapping = ADP_DB.load_df(session=session, table_name='customers')
    parent_accounts = SCA_DB.load_df(session=session, table_name='customers')
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
    customer_parts = customer_parts[['description', 'part_number', 'pkg_qty', part_price_col]]
    ## footer
    try:
        payment_terms = footer['terms'].item()
        pre_paid_freight = footer['ppf'].item()
        effective_date = str(footer['effective_date'].item())
    except:
        logger.info(f"footer capture failed for {alias_name}")
        payment_terms = None
        pre_paid_freight = None
        effective_date = '1900-01-01 00:00:00'
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
    logo_filename = parent_accounts.loc[parent_accounts['id'] == alias_mapping['sca_id'].item(), 'logo'].item()
    if not logo_filename:
        logo_filename = ''
    full_logo_path = os.path.join(LOGOS_DIR, logo_filename)
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
        session: Session,
        customer_id: int,
        stage: Stage
    ) -> ProgramFile:
    tables = ["coil_programs", "ah_programs", "program_ratings"]
    coil_prog_table, ah_prog_table, ratings = [ADP_DB.load_df(session=session, table_name=table, customer_id=customer_id) for table in tables]
    match stage:
        case Stage.ACTIVE:
            active_coils = coil_prog_table['stage'] == stage.name
            active_ahs = ah_prog_table['stage'] == stage.name
            coil_prog_table = coil_prog_table[active_coils]
            ah_prog_table = ah_prog_table[active_ahs]
        case Stage.PROPOSED:
            active_coils = coil_prog_table['stage'] == Stage.ACTIVE.name
            active_ahs = ah_prog_table['stage'] == Stage.ACTIVE.name
            proposed_coils = coil_prog_table['stage'] == stage.name
            proposed_ahs = ah_prog_table['stage'] == stage.name
            coil_prog_table = coil_prog_table[(active_coils) | (proposed_coils)]
            ah_prog_table = ah_prog_table[(active_ahs) | (proposed_ahs)]
        case _:
            raise EmptyProgram

    try:
        coil_prog = build_coil_program(coil_prog_table, ratings)
        ah_prog = build_ah_program(ah_prog_table, ratings)
        full_program = add_customer_terms_parts_and_logo_path(
            session=session,
            customer_id=customer_id,
            coil_prog=coil_prog,
            ah_prog=ah_prog
        )
        logger.info(f"generating {full_program}")
        for prog in full_program:
            logger.info(f'{prog} program included')
        price_book = (PriceBook(TEMPLATES, full_program)
                            .build_program(session=session)
                            .add_footer(offset=(0,1))
                            .attach_nomenclature_tab()
                            .attach_ratings()
                            .save_and_close())
        new_program_file = ProgramFile(
            file_data=price_book,
            file_name=full_program.new_file_name()
        )
    except EmptyProgram:
        raise EmptyProgram('No program data to return')
    except Exception:
        import traceback as tb
        logger.info("Error occurred while trying to generate programs")
        logger.info(tb.format_exc())
    else:
        tables.remove('program_ratings')
        try:
            update_dates_in_tables(session=session, tables=tables, customer_id=customer_id)
        except Exception as e:
            logger.warning('File Generation dates unable to be updated '
                           f'due to an error: {e}')
        return new_program_file

def update_dates_in_tables(
        session: Session,
        tables: Iterable[str],
        customer_id: int=None
    ) -> None:
    coil_update_q, ah_update_q = [f"""UPDATE {table} SET last_file_gen = :date WHERE customer_id IN :customers;""" for table in tables]
    params = {"customers": (customer_id,), "date": TODAY}
    with session:
        for q in coil_update_q, ah_update_q:
            ADP_DB.execute(session, q, params)
        session.commit()