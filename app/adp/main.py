from app.adp import prune_ratings
from app.adp.utils.workbook_factory import generate_program
from app.adp.extraction.parts import add_parts_to_program
from app.adp.extraction.models import  add_model_to_program
from app.adp.extraction.ratings import (
    update_ratings_reference,
    add_ratings_to_program,
    update_all_unregistered_program_ratings
)

# def generate_programs_file() -> None:
#     from app.db import Database
#     db = Database('adp')
#     TODAY = str(datetime.today().date())
#     with ExcelWriter(f'~/Desktop/all-sca-programs {TODAY}.xlsx') as file:
#         db.load_df('coil_programs').drop_duplicates().to_excel(file, 'Coils', index=False)
#         db.load_df('ah_programs').drop_duplicates().to_excel(file, 'Air Handlers', index=False)

# extract_models()
# add_models_to_program(adp_alias=sys.argv[2], models=models)
# add_parts_to_program(adp_alias=sys.argv[2], part_nums=part_nums)
# add_rating_to_program(adp_alias=customer, rating=rating)
# update_ratings_reference()
# generate_programs()
# generate_programs(all=True)
# generate_programs(all=True, stage='ACTIVE')
# generate_programs(all=True, stage='PROPOSED')
# generate_programs(sca_customers=customers)
# generate_programs_file()
# update_all_unregistered_program_ratings()
# prune_ratings.prune()