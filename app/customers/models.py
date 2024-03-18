from pydantic import BaseModel, Field, create_model, ConfigDict
from typing import Optional
from app.jsonapi.core_models import (
    JSONAPIVersion,
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    Pagination,
    Query
)

class CustomerResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = "customers"

class CustomerRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[CustomerResourceIdentifier]|CustomerResourceIdentifier


## Customer
# Schema
class CustomerAttributes(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    domains: Optional[list[str]] = None
    logo: Optional[str] = None
    buying_group: Optional[str] = Field(default=None, alias='buying-group')

class CustomerFilterSelector(BaseModel):
    filter_name: str = Field(default=None, alias='filter[name]')
    filter_domains: str = Field(default=None, alias='filter[domains]')
    filter_logo: str = Field(default=None, alias='filter[logo]')
    filter_buying_group: str = Field(default=None, alias='filter[buying-group]')

# Schema
class CustomerRelationships(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    customer_locations: JSONAPIRelationships = Field(alias='customer-locations')
    adp_customers: JSONAPIRelationships = Field(alias='adp-customers')
    adp_customer_terms: JSONAPIRelationships = Field(alias='adp-customer-terms') 

class CustomerRelationshipsFieldsSelectors(BaseModel):
    fields_customer_locations: str = Field(default=None, alias='fields[customer-locations]')
    fields_adp_customers: str = Field(default=None, alias='fields[adp-customers]')
    fields_adp_customer_terms: str = Field(default=None, alias='fields[adp-customer-terms]')

class CustomerResourceObject(CustomerResourceIdentifier):
    attributes: CustomerAttributes
    relationships: CustomerRelationships

class CustomerResponse(BaseModel):
    jsonapi: JSONAPIVersion
    meta: Optional[dict] = {}
    data: Optional[list[CustomerResourceObject]|CustomerResourceObject]
    included: Optional[list[JSONAPIResourceObject]] = None
    links: Optional[Pagination] = None

class RelatedCustomerResponse(CustomerResponse):
    """When pulling as a related object, included is always empty
        and links are not in the object"""
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)

_CustomerQuery: type[BaseModel] = create_model(
    'CustomerQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f"fields_customers":(Optional[str], None)},
    **{f"fields_{field}":(Optional[str], None) for field in CustomerRelationships.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in CustomerAttributes.model_fields.keys()},
)
class CustomerQuery(_CustomerQuery):
    ...