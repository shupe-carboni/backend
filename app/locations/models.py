
from pydantic import BaseModel, Field
from typing import Optional
from app.jsonapi import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    Pagination
)

class LocationResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = "locations"

class LocationRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[LocationResourceIdentifier]|LocationResourceIdentifier


## Location
# Schema
class LocationRelationships(BaseModel):
    customer: JSONAPIRelationships
    customer_users: JSONAPIRelationships = Field(alias='customer-users')

class LocationResourceObject(LocationResourceIdentifier):
    attributes: None = None
    relationships: LocationRelationships

class LocationResponse(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[LocationResourceObject]]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination]

class RelatedLocationResponse(LocationResponse):
    """When pulling as a related object, included is always empty
        and links are not in the object"""
    included: dict = {}
    links: dict = Field(..., exclude=True)