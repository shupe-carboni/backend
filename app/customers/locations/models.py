from pydantic import BaseModel, Field
from typing import Optional
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    Pagination
)

class LocationResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = "sca-customer-locations"

class LocationRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[LocationResourceIdentifier]|LocationResourceIdentifier

## Location
# Schema
class LocationAttrs(BaseModel):
    hq: bool
    dc: bool
class LocationRelationships(BaseModel):
    customers: JSONAPIRelationships = Field(alias='customers')
    places: JSONAPIRelationships = Field(alias='places')
    adp_quotes: JSONAPIRelationships = Field(alias='adp-quotes')

class LocationResourceObject(LocationResourceIdentifier):
    attributes: LocationAttrs
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
    links: Optional[dict] = Field(default=None, exclude=True)