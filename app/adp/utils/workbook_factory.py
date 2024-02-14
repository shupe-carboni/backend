import os
import pandas as pd
from typing import Iterable, Literal
from datetime import datetime
from openpyxl.styles import Font, Alignment, numbers
from adp_models import Fields
from programs import CoilProgram, AirHandlerProgram, CustomerProgram
from utils.pricebook import PriceBook
from db.db import Database


TODAY = str(datetime.today().date())
SAVE_DIR = '/mnt/c/users/carbo/OneDrive/Desktop/new-progs'
TEMPLATES = './templates/template.xlsx'
db = Database('adp')

def build_coil_programs(customers: pd.Series, programs: pd.DataFrame, ratings: pd.DataFrame) -> dict[str, dict[str, list[pd.DataFrame]]]:
    coil_customers = customers
    coil_progs = programs
    progs = {customer: {'coils': list()} for customer in coil_customers}
    for customer in coil_customers:
        data = coil_progs.loc[coil_progs[Fields.ADP_ALIAS.formatted()] == customer, :]
        sca_customer_name = data[Fields.CUSTOMER.formatted()].drop_duplicates().item()
        data = data.iloc[:,1:-1]
        data = data.sort_values(by=['Category','Series','MPG','Metering','Tonnage','Width','Height']).drop_duplicates()
        prog_ratings = ratings.loc[ratings['Customer'] == sca_customer_name,:].drop(columns=['Customer'])
        progs[customer]['coils'].append(CoilProgram(customer=customer, data=data, ratings=prog_ratings))
    return progs
    
def build_ah_programs(customers: pd.Series, programs: pd.DataFrame, ratings: pd.DataFrame) -> dict[str, dict[str, list[pd.DataFrame]]]:
    ah_customers = customers
    ah_progs = programs
    progs = {customer: {'air_handlers': list()} for customer in ah_customers}
    for customer in ah_customers:
        data: pd.DataFrame = ah_progs.loc[ah_progs[Fields.ADP_ALIAS.formatted()] == customer,:]
        sca_customer_name = data[Fields.CUSTOMER.formatted()].drop_duplicates().item()
        data = data.iloc[:,1:-1]
        data['heat_num'] = data['Heat'].str.extract(r'(\d+|\d\.\d)\s*kW').fillna(0).astype(float).astype(int)
        data = data.sort_values(by=['Category','Series','MPG','Tonnage','Width','heat_num']).drop_duplicates()
        data = data.drop(columns='heat_num')
        prog_ratings = ratings.loc[ratings['Customer'] == sca_customer_name,:].drop(columns=['Customer'])
        progs[customer]['air_handlers'].append(AirHandlerProgram(customer=customer, data=data, ratings=prog_ratings))
    return progs

def add_customer_terms_parts_and_logo_path(programs: dict[str, dict[str, list]]) -> list[CustomerProgram]:
    DATABASE = Database('adp')
    footers_info = DATABASE.load_df("customer_terms")
    prog_parts = DATABASE.load_df('program_parts_expanded')
    pref_parts_customers = DATABASE.load_df('preferred_parts_customers')
    alias_mapping = DATABASE.load_df('customers')
    full_programs = list()
    ## collect full customer programs
    for customer, progs in programs.items():
        ## parts
        alias_id = alias_mapping.loc[alias_mapping['adp_alias'] == customer,'id'].drop_duplicates().item()\
            if customer in alias_mapping['adp_alias'].values else None
        if not alias_id:
            print(customer)
            raise Exception("customer not found")
        else:
            sca_customer_name: str = alias_mapping.loc[alias_mapping['adp_alias'] == customer, 'customer'].item()
        customer_parts = prog_parts.loc[prog_parts['customer_id'] == alias_id,:].drop(columns='customer_id')
        customer_preferred = customer in pref_parts_customers['adp_alias'].values
        ## specific column name for pricing is to be set
        if customer_preferred:
            part_price_col = 'preferred'
            # some "preferred" pricing is left blank, so default the price to standard pricing
            customer_parts[part_price_col] = customer_parts[part_price_col].fillna(customer_parts['standard'])
        else:
            part_price_col = 'standard'
        customer_parts = customer_parts[['part_number', 'description', 'pkg_qty', part_price_col]]
        ## footer
        footer = footers_info[footers_info['customer'] == sca_customer_name]
        try:
            payment_terms = footer['terms'].item()
            pre_paid_freight = footer['ppf'].item()
            effective_date = str(footer['effective_date'].item())
        except:
            print("footer capture failed")
            print(customer)
            print(footer)
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
        logo_path = alias_mapping.loc[alias_mapping['adp_alias'] == customer, 'logo_path'].item()
        ## program gen
        full_program = CustomerProgram(**progs, parts=customer_parts, terms=terms, logo_path=logo_path)
        full_programs.append(full_program)
    return full_programs

def combine_programs(
        coil_progs: dict[str, dict[str, list[pd.DataFrame]]],
        ah_progs: dict[str, dict[str, list[pd.DataFrame]]]
    ) -> dict[str, dict[str, list[pd.DataFrame]]]:
    all_customers = {customer for customer in coil_progs} | {customer for customer in ah_progs}
    return {customer: coil_progs.get(customer,{'coils': list()})|ah_progs.get(customer,{'air_handlers': list()}) for customer in all_customers}

def generate_programs(
        all: bool=False,
        sca_customers: dict[str,tuple]|None=None,
        stage: Literal['ACTIVE', 'PROPOSEED', 'REJECTED', 'REMOVED']=None):
    DATABASE = Database('adp')
    customers_table = DATABASE.load_df('customers')
    tables = ["coil_programs", "ah_programs", "program_ratings"]
    skipped = []
    if all:
        coil_progs, ah_progs, ratings = [DATABASE.load_df(table_name=table) for table in tables]
    elif sca_customers:
        coil_progs, ah_progs, ratings = [DATABASE.load_df(table_name=table, customers=list(sca_customers['customers'])) for table in tables]
    else:
        coil_progs, ah_progs = [DATABASE.load_df(table_name=table, is_null="last_file_gen") for table in tables[:-1]]
        ratings = DATABASE.load_df(table_name='program_ratings')
    
    if stage:
        coil_progs = coil_progs[coil_progs['stage'] == stage.upper()]
        ah_progs = ah_progs[ah_progs['stage'] == stage.upper()]

    try:
        coil_customers = coil_progs.loc[:,Fields.ADP_ALIAS.formatted()].drop_duplicates()
        ah_customers = ah_progs.loc[:,Fields.ADP_ALIAS.formatted()].drop_duplicates()
        progs = combine_programs(
            build_coil_programs(coil_customers, coil_progs, ratings),
            build_ah_programs(ah_customers, ah_progs, ratings)
        )

        all_full_programs = add_customer_terms_parts_and_logo_path(programs=progs)
        for full_program in all_full_programs:
            print(f"generating {full_program}")
            if not os.path.exists(os.path.join(SAVE_DIR, full_program.new_file_name())):
                for prog in full_program:
                    print(f'\t{prog}')
                PriceBook(TEMPLATES, full_program, save_path=SAVE_DIR)\
                    .build_program()\
                    .attach_nomenclature_tab()\
                    .attach_ratings()\
                    .attach_parts()\
                    .save_and_close()
            else:
                sca_customer_name = customers_table.loc[customers_table['adp_alias'] == full_program.customer, "customer"].item()
                skipped.append(sca_customer_name)
                print(f"File already exists for {sca_customer_name}")
    except Exception:
        import traceback as tb
        print("Error occurred while trying to generate programs")
        print(tb.format_exc())
    else:
        tables.remove('program_ratings')
        update_dates_in_tables(db=DATABASE, tables=tables, all=all, customers=sca_customers, skipped=skipped)

def update_dates_in_tables(
        db: Database,
        tables: Iterable[str],
        all: bool=False,
        customers: dict[str, tuple]|None=None,
        skipped: list=None,
    ) -> None:
    if all:
        coil_update_q, ah_update_q = [f"""UPDATE {table} SET last_file_gen = :date;""" for table in tables]
        params = {'date': TODAY}
    elif customers:
        not_skipped_customers = dict(customers=tuple([customer for customer in customers['customers'] if customer not in skipped]))
        if not_skipped_customers['customers']:
            coil_update_q, ah_update_q = [f"""UPDATE {table} SET last_file_gen = :date WHERE "Customer" IN :customers;""" for table in tables]
            params = not_skipped_customers | {"date": TODAY}
        else:
            print("No programs updated")
            return None
    else:
        coil_update_q, ah_update_q = [f"""UPDATE {table} SET last_file_gen = %s WHERE last_file_gen IS NULL;""" for table in tables]
        params = (TODAY, )

    for q in coil_update_q, ah_update_q:
        db.execute_and_commit(q, params)