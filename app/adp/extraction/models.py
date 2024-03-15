import math
import copy
import pandas as pd
import openpyxl as opxl
from enum import Enum, auto
from datetime import datetime
from openpyxl.worksheet.worksheet import Worksheet
from app.adp.adp_models import MODELS, S, Fields, ModelSeries
from app.adp.utils.validator import Validator
from app.db import ADP_DB, Stage, Session
import warnings; warnings.simplefilter('ignore')

# NOTE in `extract_models` replace with in-mem collection of files passed in from api
TODAY = str(datetime.today().date())

class ParsingModes(Enum):
    ATTRS_ONLY = auto()
    BASE_PRICE = auto()
    CUSTOMER_PRICING = auto()

class InvalidParsingMode(Exception): ...

def add_model_to_program(session: Session, adp_customer_id: int, model: str) -> int:
    record_series = parse_model_string(session, adp_customer_id, model, ParsingModes.CUSTOMER_PRICING)
    record_series['stage'] = Stage.PROPOSED.name
    with session.begin():
        return separate_by_product_type_and_commit_to_db(session=session, data=record_series)
    
def parse_model_string(session: Session, adp_customer_id: int, model: str, mode: ParsingModes) -> pd.Series:
    model_obj: ModelSeries = None
    for m in MODELS:
        if matched_model := Validator(session, model, m).is_model():
            model_obj = matched_model
    record = model_obj.record()
    record_series = pd.Series(record)
    match mode:
        case ParsingModes.CUSTOMER_PRICING:
            record_series['customer_id'] = adp_customer_id
            return price_models_by_customer_discounts(session=session, model=record_series, adp_customer_id=adp_customer_id)
        case ParsingModes.BASE_PRICE:
            return record_series
        case ParsingModes.ATTRS_ONLY:
            record_series.drop(index=Fields.ZERO_DISCOUNT_PRICE.value)
            return record_series
        case _:
            raise InvalidParsingMode


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

def price_models_by_customer_discounts(session: Session, model: pd.Series, adp_customer_id: int) -> pd.Series:
    mat_grp_discounts = ADP_DB.load_df(session=session, table_name='material_group_discounts', customer_id=adp_customer_id)
    snps = ADP_DB.load_df(session=session, table_name='snps', customer_id=adp_customer_id).drop_duplicates()

    no_disc_price = int(model['zero_discount_price'])
    mat_group: str = model['mpg']
    mat_group_disc: pd.Series = mat_grp_discounts.loc[
        (mat_grp_discounts[Fields.CUSTOMER_ID.value] == adp_customer_id)
        & (mat_grp_discounts['mat_grp'] == mat_group),
        'discount'
    ]
    mat_group_disc = mat_group_disc.item() if not mat_group_disc.empty else 0
    if not isinstance(model[Fields.PRIVATE_LABEL.value],str):
        model_num: str = model[Fields.MODEL_NUMBER.value]
    else:
        model_num: str = model[Fields.PRIVATE_LABEL.value]

    snp: pd.Series = snps.loc[
        (snps[Fields.CUSTOMER_ID.value] == adp_customer_id)
        & (snps['model'] == model_num)
        & (snps['stage'].isin([Stage.ACTIVE.name, Stage.PROPOSED.name])),
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
    model.update(result)
    return model

def separate_by_product_type_and_commit_to_db(session: Session, data: pd.Series) -> int:
    if data['motor']:
        table = 'ah_programs'
    else:
        table = 'coil_programs'

    model = data.dropna()
    model['effective_date'] = TODAY
    cols = [f'"{col}"' for col in model.index.values.tolist()]
    vals = []
    for val in model.values.tolist():
        match val:
            case int() | float():
                vals.append(str(val))
            case str():
                vals.append(f"'{val}'")
    sql = f"""INSERT INTO {table} ({','.join(cols)})
            VALUES ({','.join(vals)})
            RETURNING id;"""
    new_id = ADP_DB.execute(session=session, sql=sql, params=dict(columns=cols, values=vals)).fetchone()[0]
    return new_id

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