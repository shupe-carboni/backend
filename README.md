#### Disclaimer
>*Although public, no license has been applied to this code. Default copyright laws apply, meaning no one may reproduce, distribute, or create derivative works from this code. Under Github Terms of Service, you are allowed to view the code and fork the repository **and nothing more**.*
## Purpose
This application is a web API that serves as an extensible platform for business logic required in day-to-day operations at [Shupe, Carboni & Associates](https://shupecarboni.com) (SCA).  
  
While the primary technical purpose of the API is to serve a single client, to be developed in a separate repository, separation of the backend enables straightforward administration of data using protected admin endpoints to kick off long-running background processes or perform bulk operations that are impractical to do through a web app, or not supported by its design.  

The purpose behind the development of all features offered by this API is to automate business processes wherever possible.
## Hosting
Currently hosted at [https://api.shupecarboni.com](https://api.shupecarboni.com), powered by AWS Elastic Beanstalk (EC2 and RDS).
## Auth
Authentication and Authorization is handled via Auth0, using JWT validation and the extraction of JWT body contents.  
Permissions set on users registered in Auth0 (i.e. vendors:sca-employee) are delivered to the API via Auth0 JWTs, and the API
## Organization

#### JSON:API
Routes and responses follow, as much as reasonably possible, the JSON:API specification.

HTTP requests on resources follow this general format  
&emsp;**<span style="color: green">GET</span> &emsp; /{resource}** &emsp; the full collection of objects, unless a filter is applied  
&emsp;**<span style="color: green">GET</span> &emsp; /{resource}/{id}** &emsp; a single resource object  
&emsp;**<span style="color: magenta">POST</span> &emsp;/{resource}** &emsp; create a single new resource object  
&emsp;**<span style="color: #FFD700">PATCH</span> &emsp; /{resource}/{id}** &emsp; modify a single resource  
&emsp;**<span style="color: red">DELETE</span> &emsp; /{resource}/{id}** &emsp; remove a resource  

Relationships between resources are represented in routes that follow these formats  
&emsp;**<span style="color: green">GET</span> /{resource}/{id}/{related_resource}** (Related Resource Object)  
&emsp;**<span style="color: green">GET</span> /{resource}/{id}/relationship/{related_resource}** (Relationship Object)

*See here for more --> [JSON:API](https://jsonapi.org)*

#### Conceptual example of vendor resources
Vendor resources start at the top level. Vendors have their own approaches to pricing, definitions for customers (i.e. the entire corporation vs. specific locations), customer payment terms, model numbers, and project quotes. All resources other than "Customers" for any given vendor ought to be understood as related to their "Customers" resource.
```
top-level
|
+-- ADP
|	+-- Customers
|	+-- Coils
|	+-- Air Handlers
|	+-- Parts
|	+-- Ratings
|	+-- Quotes
|	+-- (helper modules)
+-- Friedrich
|	+-- Customers
|	+-- Pricing
|	+-- Quotes
...
```
There are other resources specific to SCA used for connecting and managing entities - customers and vendors. This is especially important for customers, who are represented in as many different ways as there are vendors. Here, customers have unified identities. All "Customers" resources contained within vendor resources are related to the customer entity defined under this top-level "Customers" resource.

```
top-level
|
...
|
+-- Customers
|	+-- customers		<-- considered the "Shupe Carboni" name
|	+-- relationships
|	|	+-- customer-locations
|	|	+-- adp-customers
|	|	+-- adp-customer-terms
|	|	+-- adp-quotes
|	|	+-- ...
+-- Vendors
|	+-- Vendors	<-- hq location, phone number, contacts, etc.
|	+-- Info	<-- frieght paid amount, warranty policies - related to "Vendors"
_
```
## Administrative Capabilities
Employees and Administrators of Shupe, Carboni & Associates, (as defined by authentication token permissions, i.e. vendors:sca-employee) fall into one of two types, sca-employee or sca-admin. These two permission types share much, but not all, of the same capabilities.

By resource these capabilities are:
- **Vendors**
	- Update basic vendor information, such as current lead times and freight policies
- **Customers**
	- View Customer profiles that include information such as associated users, management groups, admin users, locations, associated quotes & pricing, etc.
	- Edit Customer profiles by updating basic information, adding locations, editing pricing, adding/editing quotes.
- **Quotes**
	- View, Edit, and Add job quotes for customers
- **ADP Resources**
	- View, Edit, Add, and Remove customer pricing and/or model numbers offered.
	- View, Add, and Remove, AHRI ratings associated with customers
	- Download customer program files as Excel documents
## Customer Capabilities
Customers may fall into one of several user types (as defined by authentication token permissions)
- Admin
- Manager
- Standard

### Admin
#### *{resource}:customer-admin*
Admin customers can see all resources associated with their parent customer profile, regardless of location.  
Admin customers can manage users associated with their same customer account, such as assigning users to management permissions, assigning branches to their management group, and adding and removing users.

### Manager
#### *{resource}:customer-manager*
Manager Customers can see and manage all resources associated with their management group, which are a collection of customer locations.

### Standard
#### *{resource}:customer-std*
Standard customers can see and manage all resources associated with the their location (i.e. their branch).