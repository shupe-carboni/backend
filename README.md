#### Disclaimer
>*Although public, no license has been applied to this code. Default copyright laws apply, meaning no one may reproduce, distribute, or create derivative works from this code. Under Github Terms of Service, you are allowed to view the code and fork the repository **and nothing more**.*
## Purpose
This application is a web API that serves as an extensible platform for business logic required in day-to-day customer service operations at [Shupe, Carboni & Associates](https://shupecarboni.com) (SCA).  

This API serves several client types, including a web application and a terminal application. 

## Hosting
Currently hosted at [https://api.shupecarboni.com](https://api.shupecarboni.com), powered by AWS Elastic Beanstalk (EC2 and RDS).
## Auth
Authentication and Authorization is handled via Auth0, using JWT validation and the extraction of JWT body contents.  
Permissions set on users registered in Auth0 (i.e. sca-employee or customer-manager) are delivered to the API via Auth0 JWTs, and the API
## Organization

#### JSON:API
Routes and responses follow, as much as reasonably possible, the JSON:API specification.

HTTP requests on resources follow this general format  
&emsp;**<span style="color: green">GET</span> &emsp; /{resource}** &emsp; the full collection of objects, unless a filter is applied  
&emsp;**<span style="color: green">GET</span> &emsp; /{resource}/{id}** &emsp; a single resource object  
&emsp;**<span style="color: magenta">POST</span> &emsp;/{resource}** &emsp; create a single new resource object  
&emsp;**<span style="color: #FFD700">PATCH</span> &emsp; /{resource}/{id}** &emsp; modify a single resource  
&emsp;**<span style="color: red">DELETE</span> &emsp; /{resource}/{id}** &emsp; remove a resource  

Relationships between resources are represented in routes that follow these formats  :w

&emsp;**<span style="color: green">GET</span> /{resource}/{id}/{related_resource}** (Related Resource Object)  
&emsp;**<span style="color: green">GET</span> /{resource}/{id}/relationship/{related_resource}** (Relationship Object)

However, one major departure is in query paramters, which are explicitly defined and entirely in snake_case, instead of the format in the spec.
*See here for more --> [JSON:API](https://jsonapi.org)*

#### Conceptual example of vendor resources
Vendor resources start at the top level. Vendors have their own approaches to pricing, definitions for customers (i.e. the entire corporation vs. specific locations), customer payment terms, model numbers, and project quotes. All resources under a vendor other than "Customers" are related to their "Customers" resource and sub-resources are in turn related to their parent, such as 'Products' under 'Quotes'. 
```
top-level
|
+-- ADP
|	+-- Adp-Customers
|	+-- Adp-Coil-Programs		<-- related to "Customers"
|	+-- Adp-Ah-Programs
|	+-- Adp-Program-Parts
|	+-- Adp-Program-Ratings
|	+-- Adp-Quotes				<-- related to "Customers"
|	|	+-- Adp-Quote-Products	<-- related to "Quotes"
|
+-- (additional vendors)
|	+-- Customers
|	+-- Pricing
|	+-- Quotes
|	|	+-- Products
|
|	...
```
There are other resources specific to SCA used for connecting and managing entities - customers and vendors. This is important for customers, who are represented in as many different ways as there are vendors. Here, customers have unified identities. All "Customers" resources contained within vendor resources are related to the customer entity defined under this top-level "Customers" resource.

```
top-level
|
+-- Customers
|	+-- Customers			<-- considered the "Shupe Carboni" customer entity name
|	+-- Customer-Locations	<-- related to "Customers" and the connection point for vendor representations of customers 
|	+-- Adp-Customers		<-- related to "Customer-Locations" via a mapping table
|	+-- Adp-Customer-Terms
|	+-- Adp-Quotes
|	+-- ...
+-- Vendors
|	+-- Vendors				<-- hq location, phone number, contacts, etc.
|	+-- Info				<-- frieght paid amount, warranty policies - related to "Vendors"
_
```
> Although the Vendors resource is separated from the specific vendor resources like ADP, url paths are consistent with the expecation that one can view the `info` related a vendor the same way as the vendor resources themselves, i.e. `/vendors/adp/info` and `/vendors/adp/adp-coil-programs` respectively. 
## Description of Resources

- **Vendors**
	- Basic vendor information, such as current lead times, freight policies, and warranty policies.
	- Not specific to customers
- **Customers**
	- Customer profiles include information such as associated users, management groups, locations (sometimes called "braches").
	- Independent of vendor names and id numbers, specific to SCA's representation of customer entities.
- **ADP**
	- Customer pricing, payment terms, and project quotes.
	- Requests for new project quotes.
	- AHRI ratings associated with product stategies
	- Download customer product strategy files as stylized Excel documents

## Customer Capabilities
Customers may fall into one of several user types (as defined by authentication token permissions)
- Admin
- Manager
- Standard

### Admin
#### *customer-admin*
Admin customers can see all resources associated with their parent customer profile, regardless of location.  
Admin customers can manage users associated with their same customer account, such as assigning users to management permissions, assigning branches to their management group, and adding and removing users.

### Manager
#### *customer-manager*
Manager Customers can see and manage all resources associated with their management group, which are a collection of customer locations.

### Standard
#### *customer-std*
Standard customers can see and manage all resources associated with the their location (i.e. their branch).