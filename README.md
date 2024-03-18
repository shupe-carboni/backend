## Purpose
This application is a web API that serves as an extensible platform for business logic required in day-to-day operations at [Shupe, Carboni & Associates](https://shupecarboni.com).  
While the primary technical purpose of the API is to serve a single client, to be developed in a separate repository, separation of the backend enables straightforward administration of data using protected admin endpoints to kick off long-running background processes or perform bulk operations that are impractical to do through a web app, or not supported by its design.  

The purpose behind the development of all features offered by this API is to automate business processes wherever possible.

## Administrative Capabilities
Employees and Administrators of Shupe, Carboni & Associates, (as defined by authentication token permissions, i.e. vendors:sca-employee) can  
* Vendors
	- Update basic vendor information, such as current lead times and freight policies
* Customers
	- View Customer profiles that include information such as associated users, management groups, admin users, locations, associated quotes & pricing, etc.
	- Edit Customer profiles by updating basic information, adding locations, editing pricing, adding/editing quotes.
* Quotes
	- View, Edit, and Add job quotes for customers
* ADP Resources
	- View, Edit, Add, and Remove customer pricing programs.
	- View, Add, and Remove, AHRI ratings for customers
	- Download customer program files as Excel documents

## Customer Capabilities
Customers may fall into one of several user types (as defined by authentication token permissions)
* Admin
* Manager
* Standard

### Admin
Admin customers can see all resources associated with their parent customer profile, regardless of location.  
Admin customers can manage users associated with their same customer account, such as assigning users to management permissions, assigning branches to their management group, and adding and removing users.

### Manager
Manager Customers can see and manage all resources associated with their management group, which are a collection of customer locations.

### Standard
Standard customers can see and manage all resources associated with the their location (i.e. their branch).

## ADP Resources
<>