# Friedrich Air Conditioning
## Pricing
Pricing for customers has two components that come from pricing references (`pricing-reference`):
1. Price Level Pricing: Non-stocking, Stocking, and Standard (`friedrich-pricing`)
2. Special Pricing: Certain accounts with their own pricing that does not aligh with a price level (`friedrich-pricing-special`)

Customers add/remove products from either these into their curated price lists (`pricing-customer`)
* Friedrich Pricing Customer (`friedrich-pricing-customer`)
* Friedrich Pricing Special Customer (`friedrich-pricing-special-customer`)

*These tables are mapping tables, just associating id numbers between customers and pricing records, like a favorites list, so that the customer can view a subset of their entire universe of pricing.*

A mapping table is used behind the scenes such that hitting the price reference endpoint, such as `/vendors/friedrich/friedrich-pricing`, will automatically filter results based on the assignment of the customer to a price level, whereas special pricing is explicitly tied to customers.

The price level is represented as an enum (`NON_STOCKING`,`STOCKING`,`STANDARD`), and customer assignments can be managed through `/vendors/friedrich/friedrich-customer-price-levels`, a `pricing-mapping` resource
## Products
Friedrich maintains a full catalog of products. The product table maps to `friedrich-pricing`, `friedrich-pricing-special`, and `friedrich-quote-products`.  

Only the Friedrich model number and the description are captured within this table. There are no other feature fields that would be specific to particular products (i.e. BTUs)
## Quotes
Project quotes generated on the front end through a multi-step form are stored in two separate tables
1. A quotes table with metadata about the quote itself (`friedrich-quotes`)
2. A quotes products table related to the quotes table (`friedrich-quote-products`)

Customer input for the model to quote against is stored as the `tag`, which can be the competitor model number, the tag for the units on the plan, or a short desciption. Customers also put in the quantities, stored as `qty`.

If plans are available, they are uploaded to Amazon S3, and the relative path to that file is stored in `plans-doc`. Likewise, official documents that come back from Friedrich as the official quote are uploaded to Amazon S3 and the path is stored in `quote-doc`.