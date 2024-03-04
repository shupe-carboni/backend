from pydantic import BaseModel, Field, create_model
from typing import Optional
from app.jsonapi import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    Pagination,
    Query
)

class CustomerResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = "sca-customers"

class CustomerRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[CustomerResourceIdentifier]|CustomerResourceIdentifier


## Customer
# Schema
class CustomerAttributes(BaseModel):
    name: str
    domains: Optional[list[str]] = []
    logo: Optional[str] = None
    buying_group: str = Field(default=None, alias='buying-group')
    class Config:
        populate_by_name = True

# Schema
class CustomerRelationships(BaseModel):
    sca_customer_locations: JSONAPIRelationships = Field(alias='sca-customer-locations')
    adp_customers: JSONAPIRelationships = Field(alias='adp-customers')
    adp_customer_terms: JSONAPIRelationships = Field(alias='adp-customer-terms') 
    class Config:
        populate_by_name = True

class CustomerResourceObject(CustomerResourceIdentifier):
    attributes: CustomerAttributes
    relationships: CustomerRelationships

class CustomerResponse(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[CustomerResourceObject]]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination]

class RelatedCustomerResponse(CustomerResponse):
    """When pulling as a related object, included is always empty
        and links are not in the object"""
    included: dict = {}
    links: dict = Field(..., exclude=True)

CustomerQuery: type[BaseModel] = create_model(
    'CustomerQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f"fields_{field}":(Optional[str], None) for field in CustomerRelationships.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in CustomerAttributes.model_fields.keys()},
)