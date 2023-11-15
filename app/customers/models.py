from pydantic import BaseModel, Field
from typing import Optional
from app.jsonapi import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    Pagination
)

class CustomerResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = "customers"

class CustomerRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[CustomerResourceIdentifier]|CustomerResourceIdentifier


## Customer
# Schema
class CustomerAttributes(BaseModel):
    name: str
    domains: list[str]

# Schema
class CustomerRelationships(BaseModel):
    locations: JSONAPIRelationships

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