#### Disclaimer
>~~*Although public, no license has been applied to this code. Default copyright laws apply, meaning no one may reproduce, distribute, or create derivative works from this code. Under Github Terms of Service, you are allowed to view the code and fork the repository **and nothing more**.*~~

See LICENSE

## Purpose
This application is an API that serves as an extensible platform for business logic required in day-to-day customer service operations at [Shupe, Carboni & Associates](https://shupecarboni.com) (SCA).  

This API serves several client types, including a web application and a terminal application. 
## Hosting
Hosted at [https://api.shupecarboni.com](https://api.shupecarboni.com), powered by AWS Elastic Beanstalk (EC2 and RDS).
## Auth
Authentication and Authorization is handled via Auth0, using JWT validation and the extraction of JWT body contents.  
Permissions set on users registered in Auth0 (i.e. sca-employee or customer-manager) are delivered to the API via Auth0 JWTs, and the API
## Organization and Request-Response Style

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

As of version 2, `GET` requests on certain resources may be chained with respect to the vendor, such as `/{vendor}/{resource_1}/.../{resource_N}`. This is done for filtering against the vendor and logical consistency of relationships.