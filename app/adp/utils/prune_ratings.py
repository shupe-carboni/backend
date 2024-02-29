import re
import pandas as pd
from app.db import ADP_DB


# coil_models_by_customer = db.load_df('coil_programs')
# ah_models_by_customer = db.load_df('ah_programs')
# ratings_by_customer = db.load_df('program_ratings')

def prune() -> None:
    coil_models_by_customer = coil_models_by_customer.loc[:, ((coil_models_by_customer.columns.str.contains('ratings')) | (coil_models_by_customer.columns.isin(['customer'])))]
    ah_models_by_customer = ah_models_by_customer.loc[:, ((ah_models_by_customer.columns.str.contains('ratings')) | (ah_models_by_customer.columns.isin(['customer'])))]

    coil_models_by_customer = coil_models_by_customer.drop_duplicates()
    ah_models_by_customer = ah_models_by_customer.drop_duplicates()

    def mark_to_keep(row: pd.Series) -> bool:
        customer = row['customer']
        indoormodel = row['IndoorModel']
        if indoormodel is None:
            indoormodel = row['Coil Model Number']
            if indoormodel is None:
                return False
        coil_ratings_regexes = coil_models_by_customer.loc[coil_models_by_customer['customer'] == customer, coil_models_by_customer.columns.str.contains('ratings')].drop_duplicates().dropna().unstack()
        ah_ratings_regexes = ah_models_by_customer.loc[ah_models_by_customer['customer'] == customer, ah_models_by_customer.columns.str.contains('ratings')].drop_duplicates().dropna().unstack()
        customer_regexes = pd.concat([coil_ratings_regexes, ah_ratings_regexes]).values
        for regex in customer_regexes:
            rating_model = re.compile(regex)
            if rating_model.match(indoormodel):
                return True
        return False

    # ratings_by_customer['keep'] = ratings_by_customer.apply(mark_to_keep, axis=1)
    # the_pruned_ids = ratings_by_customer.loc[ratings_by_customer['keep'] == False, 'id']
    # sql = """DELETE FROM program_ratings WHERE id = :record_id"""
    # for id in the_pruned_ids.values:
    #     print(f"removing rating with id {id}")
    #     db.execute_and_commit(sql=sql, params={'record_id': int(id)})
    # ratings_by_customer.to_csv('/mnt/c/users/carbo/OneDrive/Desktop/ratings-pruning.csv')