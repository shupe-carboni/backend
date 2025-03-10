import os

from app.admin.price_updates import price_updates

dir_name = os.path.dirname(os.path.abspath(__file__))
pricing_by_class: str = "pricing_by_class_json.sql"
pricing_by_customer: str = "pricing_by_customer_json.sql"
with open(os.path.join(dir_name, pricing_by_class)) as f:
    pricing_by_class = f.read()
with open(os.path.join(dir_name, pricing_by_customer)) as f:
    pricing_by_customer = f.read()
