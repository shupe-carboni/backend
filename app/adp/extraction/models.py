import re
import math
import os
import copy
import pandas as pd
import openpyxl as opxl
from datetime import datetime
from openpyxl.worksheet.worksheet import Worksheet
from app.adp.adp_models import MODELS, S, Fields, ModelSeries
from app.adp.utils.validator import Validator
from app.db import ADP_DB, Stage, Session
import warnings; warnings.simplefilter('ignore')

# NOTE in `extract_models` replace with in-mem collection of files passed in from api
TODAY = str(datetime.today().date())

def extract_models_from_sheet(session: Session, sheet: Worksheet) -> list[ModelSeries]:
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
                if model_clean := Validator(session, val, m).is_model():
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

def extract_models_from_file(session: Session, file: str) -> set[ModelSeries]:
    wb = opxl.load_workbook(file)
    models = list()
    for sheet in wb.worksheets:
        models.extend(extract_models_from_sheet(session=session, sheet=sheet))
    return set(models)

def price_models_by_customer_discounts(session: Session, program_data: pd.DataFrame):
    mat_grp_discounts = ADP_DB.load_df(session=session, table_name='material_group_discounts')
    snps = ADP_DB.load_df(session=session, table_name='snps').drop_duplicates()

    def calc_prices(data: pd.Series) -> pd.Series:
        no_disc_price = int(data['zero discount price'])
        adp_alias = data['adp_alias']
        mat_group: str = data['mpg']
        mat_group_disc: pd.Series = mat_grp_discounts.loc[
            (mat_grp_discounts['adp_alias'] == adp_alias)
            & (mat_grp_discounts['mat_grp'] == mat_group),
            'discount'
        ]
        mat_group_disc = mat_group_disc.item() if not mat_group_disc.empty else 0
        model_num: str = data['model_number']
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
            Fields.MATERIAL_GROUP_DISCOUNT.value: mat_group_disc if mat_group_disc else None,
            Fields.MATERIAL_GROUP_NET_PRICE.value: mat_group_price if mat_group_price else None,
            Fields.SNP_DISCOUNT.value: snp_disc if snp_disc else None,
            Fields.SNP_PRICE.value: snp if snp else None,
            Fields.NET_PRICE.value: min([price for price in (snp, mat_group_price, no_disc_price) if price])
        }
        return pd.Series(result)

    program_data[
        [Fields.MATERIAL_GROUP_DISCOUNT.value,
         Fields.MATERIAL_GROUP_NET_PRICE.value,
         Fields.SNP_DISCOUNT.value,
         Fields.SNP_PRICE.value,
         Fields.NET_PRICE.value
        ]] = program_data.apply(calc_prices, axis=1, result_type='expand')

    return
    
def separate_product_types_and_commit_to_db(session: Session, data: pd.DataFrame):
    ah_filter = data['motor'].isna()
    coil_progs = data[ah_filter].dropna(axis=1, how='all')
    ah_progs = data[~ah_filter].dropna(axis=1, how='all')
    coil_progs['effective date'] = TODAY
    ah_progs['effective date'] = TODAY
    ADP_DB.upload_df(session=session, data=coil_progs, table_name='coil_programs', if_exists='append')
    ADP_DB.upload_df(session=session, data=ah_progs, table_name='ah_programs', if_exists='append')

def add_models_to_program(session: Session, adp_alias: str, models: list[str]) -> None:
    aliases = ADP_DB.load_df(session=session, table_name='customers', customer_id=[adp_alias])[['customer', 'adp_alias']]
    sca_customer_name = aliases.loc[aliases['adp_alias'] == adp_alias, 'customer'].drop_duplicates().item()
    model_objs: set[ModelSeries] = set()
    for model in models:
        for m in MODELS:
            if model_obj := Validator(session, model, m).is_model():
                model_objs.add(model_obj)
    records = [model.record() for model in model_objs]
    df = pd.DataFrame.from_records(data=records).dropna(how="all").drop_duplicates()
    df['adp_alias'] = adp_alias
    price_models_by_customer_discounts(session=session, program_data=df)
    df['customer'] = sca_customer_name
    df['stage'] = Stage.PROPOSED.name
    with session.begin():
        separate_product_types_and_commit_to_db(session=session, data=df)
    return

def reprice_programs(session: Session) -> None:
    aliases = ADP_DB.load_df(session=session, table_name='customers')[['customer', 'adp_alias']]
    for customer in aliases.itertuples():
        sca_customer_name = customer.customer
        adp_customer_name = customer.adp_alias
        for table in ('coil_programs', 'ah_programs'):
            prog_data = ADP_DB.load_df(session=session, table_name=table)
        ...

    # def get_sales(data: pd.Series) -> pd.Series:
    #     prog: str = data['program']
    #     adp_alias = progs_to_alias.loc[progs_to_alias['program'] == prog, 'adp_alias']
    #     adp_alias = adp_alias.item() if not adp_alias.empty else None
    #     if not adp_alias:
    #         return pd.Series({'sales 2022': 0, 'sales 2023': 0, 'total': 0})
    #     model_num: str = data['model_number']
    #     mat_group: str = data['mpg']
    #     model_sales = sales.loc[
    #         (sales['CustName'] == adp_alias)
    #         & (sales['Description'] == model_num)
    #         & (sales['MG'] == mat_group),
    #         ['Year', 'Sales']
    #     ]
    #     if model_sales.empty:
    #         return pd.Series({'sales 2022': 0, 'sales 2023': 0, 'total': 0})
    #     model_sales_by_year = model_sales.groupby('Year')['Sales'].sum().sort_index(ascending=True)
    #     if 2022 not in model_sales_by_year.index:
    #         model_sales_by_year['2022'] = 0
    #     if 2023 not in model_sales_by_year.index:
    #         model_sales_by_year['2023'] = 0
    #     model_sales_by_year.index = [f'sales_{year}' for year in model_sales_by_year.index]
    #     model_sales_by_year['total'] = model_sales_by_year.sum()
    #     model_sales_by_year = model_sales_by_year.apply(lambda val: f'{val:.2f}')
    #     return model_sales_by_year
    

    # program_data[
    #     [Fields.SALES_2022.value,
    #      Fields.SALES_2023.value,
    #      Fields.TOTAL.value,
    #     ]] = program_data.apply(get_sales, axis=1, result_type='expand')