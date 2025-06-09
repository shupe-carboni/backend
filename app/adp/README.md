# Advanced Distributor Products (ADP)

API Features unique to ADP
* Product Strategy File Generation
* Building new models
* Validating Model numbers against specification constraints (not implemented)

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
ADP's products are custom built. There is no current list of every product that can
be made. Most product configurations are not likely to ever be used (i.e. coil cabinet
paint colors with refrigerant connections on the same side as the OEM's furnace flue).

## Validating Model Numbers
This functionality has not been implemented yet. Product contraints have been loaded
in `/app/adp/products`, but are not currently used to validate input for new
product creation.