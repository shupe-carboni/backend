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

# Schema
class CustomerRelationships(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    customer_locations: JSONAPIRelationships = Field(alias='customer-locations')
    adp_customers: JSONAPIRelationships = Field(alias='adp-customers')
    adp_customer_terms: JSONAPIRelationships = Field(alias='adp-customer-terms') 

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
    links: dict = Field(..., exclude=True)

CustomerQuery: type[BaseModel] = create_model(
    'CustomerQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f"fields_{field}":(Optional[str], None) for field in CustomerRelationships.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in CustomerAttributes.model_fields.keys()},
)