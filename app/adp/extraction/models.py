import re
import math
import os
import copy
import pandas as pd
import openpyxl as opxl
from datetime import datetime
from openpyxl.worksheet.worksheet import Worksheet
from adp_models import MODELS, S, Fields, ModelSeries
from utils.validator import Validator
from app.db import Database, Status
import warnings; warnings.simplefilter('ignore')

DATABASE = Database('adp')
CUSTOMERS = DATABASE.load_df('customers')
progs_to_alias = DATABASE.load_df('programs_to_customer')
TODAY = str(datetime.today().date())

def extract_models_from_sheet(sheet: Worksheet) -> list[ModelSeries]:
    """iterates over cell contents
        and uses Validator to see if the content appears to be
        a valid ADP part number.
        If content matches, add it to a list of model objects

        model_clean: ModelSeries

        Returns: list[ModelSeries]
        """
    models = list()
    for row in sheet:
        for col in range(8):
            try:
                val = row[col].value
            except IndexError:
                break
            for m in MODELS:
                if model_clean := Validator(val, m).is_model():
                    if isinstance(model_clean, S):
                        if model_clean.get('heat') == 'XX':
                            for heat_option in ('05', '07', '10'):
                                model_variant = copy.deepcopy(model_clean)
                                model_variant['heat'] = heat_option
                                models.append(model_variant)
                        else:
                            models.append(model_clean) 
                    else:
                        models.append(model_clean)
    return models

def extract_models_from_file(file: str) -> set[ModelSeries]:
    wb = opxl.load_workbook(file)
    models = list()
    for sheet in wb.worksheets:
        models.extend(extract_models_from_sheet(sheet=sheet))
    return set(models)

def extract_all_programs_from_dir(dir: str) -> pd.DataFrame:
    data: dict[str, dict[str, set[ModelSeries]]] = dict()
    for root, _, files in os.walk(dir):
        for file in files:
            program: str = os.path.basename(file).replace('.xlsx','')
            program = re.sub(r'\d{4}-\d{1,2}-\d{1,2}', '', program).strip()
            results = extract_models_from_file(os.path.join(root,file))
            if not data.get(program):
                data[program] = {'models': set()}
            data[program]['models'] |= results
    dfs = []
    for program in data:
        records = [record.record() for record in data[program]['models']]
        df = pd.DataFrame.from_records(data=records).dropna(how="all").drop_duplicates()
        if df.isna().all().all():
            pass
        df['Program'] = program
        dfs.append(df)
    result = pd.concat(dfs).sort_values(by=['Program','Category','Series','MPG','Tonnage','Width'])
    return result
        
def price_models_by_customer_discounts(program_data: pd.DataFrame):
    mat_grp_discounts = DATABASE.load_df('material_group_discounts')
    snps = DATABASE.load_df('snps').drop_duplicates()
    # sales['Description'] = sales['Description'].str.extract(r'^([^ ]+)')
    # sales['CustName'] = sales['CustName'].str.replace(r'^WINSUPPLY.*', 'WINSUPPLY', regex=True)
    # sales['CustName'] = sales['CustName'].str.replace(r'.*WINAIR$', 'WINSUPPLY', regex=True)

    def calc_prices(data: pd.Series) -> pd.Series:
        no_disc_price = int(data['Zero Discount Price'])
        if 'adp_alias' in data.index:
            adp_alias = data['adp_alias']
            has_alias = True
        else:
            prog: str = data['Program']
            adp_alias = progs_to_alias.loc[progs_to_alias['program'] == prog, 'adp_alias']
            if adp_alias.empty:
                has_alias = False
            else:
                adp_alias = adp_alias.item()
                has_alias = True
        
        if not has_alias:
            mat_group_disc = 0
            mat_group_price = 0
            snp = 0
            snp_disc = 0
        else:
            mat_group: str = data['MPG']
            mat_group_disc: pd.Series = mat_grp_discounts.loc[
                (mat_grp_discounts['adp_alias'] == adp_alias)
                & (mat_grp_discounts['mat_grp'] == mat_group),
                'discount'
            ]
            mat_group_disc = mat_group_disc.item() if not mat_group_disc.empty else 0
            model_num: str = data['Model Number']
            snp: pd.Series = snps.loc[
                (snps['adp_alias'] == adp_alias)
                & (snps['model'] == model_num),
                'price'
            ]
            snp = snp.item() if not snp.empty else 0
            snp_disc = f'{(1 - (snp / no_disc_price)) * 100:.1f}' if snp else 0
            mat_group_price = no_disc_price * (1 - mat_group_disc / 100)
            mat_group_price = int(math.floor(mat_group_price + 0.5))
            mat_group_price = 0 if mat_group_price == no_disc_price else mat_group_price
        result = {
            Fields.MATERIAL_GROUP_DISCOUNT.formatted(): mat_group_disc if mat_group_disc else None,
            Fields.MATERIAL_GROUP_NET_PRICE.formatted(): mat_group_price if mat_group_price else None,
            Fields.SNP_DISCOUNT.formatted(): snp_disc if snp_disc else None,
            Fields.SNP_PRICE.formatted(): snp if snp else None,
            Fields.NET_PRICE.formatted(): min([price for price in (snp, mat_group_price, no_disc_price) if price])
        }
        return pd.Series(result)

    program_data[
        [Fields.MATERIAL_GROUP_DISCOUNT.formatted(),
         Fields.MATERIAL_GROUP_NET_PRICE.formatted(),
         Fields.SNP_DISCOUNT.formatted(),
         Fields.SNP_PRICE.formatted(),
         Fields.NET_PRICE.formatted()
        ]] = program_data.apply(calc_prices, axis=1, result_type='expand')

    return
    
    ## sales calcuation cut out of the method above ^^ ##

    # def get_sales(data: pd.Series) -> pd.Series:
    #     prog: str = data['Program']
    #     adp_alias = progs_to_alias.loc[progs_to_alias['program'] == prog, 'adp_alias']
    #     adp_alias = adp_alias.item() if not adp_alias.empty else None
    #     if not adp_alias:
    #         return pd.Series({'Sales 2022': 0, 'Sales 2023': 0, 'Total': 0})
    #     model_num: str = data['Model Number']
    #     mat_group: str = data['MPG']
    #     model_sales = sales.loc[
    #         (sales['CustName'] == adp_alias)
    #         & (sales['Description'] == model_num)
    #         & (sales['MG'] == mat_group),
    #         ['Year', 'Sales']
    #     ]
    #     if model_sales.empty:
    #         return pd.Series({'Sales 2022': 0, 'Sales 2023': 0, 'Total': 0})
    #     model_sales_by_year = model_sales.groupby('Year')['Sales'].sum().sort_index(ascending=True)
    #     if 2022 not in model_sales_by_year.index:
    #         model_sales_by_year['2022'] = 0
    #     if 2023 not in model_sales_by_year.index:
    #         model_sales_by_year['2023'] = 0
    #     model_sales_by_year.index = [f'Sales {year}' for year in model_sales_by_year.index]
    #     model_sales_by_year['Total'] = model_sales_by_year.sum()
    #     model_sales_by_year = model_sales_by_year.apply(lambda val: f'{val:.2f}')
    #     return model_sales_by_year
    

    # program_data[
    #     [Fields.SALES_2022.formatted(),
    #      Fields.SALES_2023.formatted(),
    #      Fields.TOTAL.formatted(),
    #     ]] = program_data.apply(get_sales, axis=1, result_type='expand')


def set_customer_name(program: str) -> str|None:
    adp_alias_1 = progs_to_alias.loc[progs_to_alias['program'] == program, 'adp_alias']
    adp_alias = adp_alias_1.item() if not adp_alias_1.empty and not adp_alias_1.isna().any() else None
    if adp_alias is None:
        return '#N/A'
    customer: str = CUSTOMERS.loc[CUSTOMERS['adp_alias'] == adp_alias,'customer'].item() if adp_alias else ''
    return customer if customer else '#N/A'

def separate_product_types_and_commit_to_db(data: pd.DataFrame):
    ah_filter = data['Motor'].isna()
    coil_progs = data[ah_filter].dropna(axis=1, how='all')
    ah_progs = data[~ah_filter].dropna(axis=1, how='all')
    coil_progs['Effective Date'] = TODAY
    ah_progs['Effective Date'] = TODAY
    DATABASE.upload_df(coil_progs, 'coil_programs', if_exists='append')
    DATABASE.upload_df(ah_progs, 'ah_programs', if_exists='append')

def extract_models() -> None:
    dir = '/home/carboni/sca-scratchspace/adp-program-reformat/old-style' # NOTE replace with in-mem collection of files passed in from api
    result = extract_all_programs_from_dir(dir=dir)
    price_models_by_customer_discounts(result)
    result.insert(0,'Customer', result['Program'].apply(set_customer_name))
    separate_product_types_and_commit_to_db(result)


def add_models_to_program(adp_alias: str, models: list[str]) -> None:
    aliases = DATABASE.load_df('customers',customers=[adp_alias], use_alias=True)[['customer', 'adp_alias']]
    sca_customer_name = aliases.loc[aliases['adp_alias'] == adp_alias, 'customer'].drop_duplicates().item()
    model_objs: set[ModelSeries] = set()
    for model in models:
        for m in MODELS:
            if model_obj := Validator(model,m).is_model():
                model_objs.add(model_obj)
    records = [model.record() for model in model_objs]
    df = pd.DataFrame.from_records(data=records).dropna(how="all").drop_duplicates()
    df['adp_alias'] = adp_alias
    price_models_by_customer_discounts(df)
    df['Customer'] = sca_customer_name
    df['stage'] = Status.PROPOSED.name
    separate_product_types_and_commit_to_db(df)

def reprice_programs() -> None:
    aliases = DATABASE.load_df('customers')[['customer', 'adp_alias']]
    for customer in aliases.itertuples():
        sca_customer_name = customer.customer
        adp_customer_name = customer.adp_alias
        for table in ('coil_programs', 'ah_programs'):
            prog_data = DATABASE.load_df(table)
        ...