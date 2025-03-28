from types import SimpleNamespace
class Queries(SimpleNamespace):
    apply_percentage_on_customer_price: str
    apply_percentage_on_class_price: str
    atco_price_updates: str
    atco_pricing_pop_temp: str
    atco_mults_temp_setup: str
    atco_mults_pop_temp: str
    atco_teardown: str
    atco_pricing_temp_setup: str
    product_series_update: str
    customer_product_class_discount_update: str
    customer_pricing_update: str
    signal_updatable_futures: str
    class_pricing_update: str
    customer_product_discount_update: str
    pricing_by_class_json: str
    pricing_by_customer_json: str
    adp_parts_establish_future: str
    adp_parts_insert_new_product: str
    adp_parts_new_product_pricing: str
    adp_parts_insert_setup_attrs_new_product: str
    adp_parts_populate_temp: str
    adp_parts_temp_table: str
    adp_zero_disc_establish_future: str
    adp_zero_disc_pop_temp: str
    adp_zero_disc_get_all_models: str
    adp_zero_disc_setup: str
    adp_zero_disc_teardown: str
    adp_customers_temp_teardown: str
    adp_customers_insert_new: str
    adp_customers_tamp_table: str
    adp_customers_pop_temp: str
    adp_discounts_establish_future: str
    adp_discounts_populate_temp: str
    adp_discounts_temp_table: str
    adp_discounts_temp_teardown: str
    adp_discounts_insert_new: str
    adp_customer_pricing_pop_temp: str
    adp_customer_pricing_teardown: str
    adp_customer_pricing_temp_setup: str
    adp_customer_pricing_establish_future: str
    adp_customer_pricing_all_models: str
    adp_snps_insert_new: str
    adp_snps_teardown: str
    adp_snps_pop_temp: str
    adp_snps_temp_table: str
    adp_snps_establish_future: str
    adp_product_series_pop_temp: str
    adp_product_series_temp_table: str
    adp_product_series_teardown: str
    adp_product_series_establish_future: str
queries: Queries