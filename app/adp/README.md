# Advanced Distributor Products (ADP)

API Features unique to ADP
* Product Strategy File Generation
* Building new models for entry into *vendor_products* and *vendor_product_attrs* tables
* Validating Model numbers against specification constraints

## Product Strategy File Generation
ADP specifies a specific format to use for delivering product information and pricing to
customers. ADP specifies an Excel file with 2 or more tabs
1. **Model List**: dimensions and pricing of all models
2. **Nomenclature**: nomenclature for all product series in the model listing, using
model numbers sampled directly from the customer's model listing
3. (Optional) **Ratings**: one or more tabs for AHRI ratings related to product in the 
model listing  
  
Templates are contained in `/app/adp/templates`.  

## Building New Models
ADP's products are custom built. There is no current list of every product that could
possibly be made. I could make one, which would product about 140,000 records, but
this would ultimately be a waste of space, as most of them would never be used.

With this reality, there needs to be a way to add new models to the vendor's product
listing efficiently, including features in the attributes table. The same functionality
used in V1 can be used here. However, the data will be saved differently. In V1, 
products were listed by-customer and included features in the table schema. In V2,
products and attributes are stored separately, and Strategy products are defined by
which entries exist in the table *vendor_pricing_by_customer*
(vendor_customer_id, vendor_product_id, price).

## Validating Model Numbers
This functionality has not been implemented yet. Product contraints have been loaded
in `/app/adp/products`, but are not currently used to validate input for new
product creation.