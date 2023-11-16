from pydantic import BaseModel, Field
from typing import Optional
from app.jsonapi import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    Pagination
)

class PlaceResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = "places"

class PlaceRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[PlaceResourceIdentifier]|PlaceResourceIdentifier

## Place
# Schema
class PlaceAttributes(BaseModel):
    name: str
    state: str
    lat: float
    long: float

# Schema
class PlaceRelationships(BaseModel):
    locations: JSONAPIRelationships
    quotes: JSONAPIRelationships

class PlaceResourceObject(PlaceResourceIdentifier):
    attributes: PlaceAttributes
    relationships: PlaceRelationships

class PlaceResponse(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[PlaceResourceObject]]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination]

class RelatedPlaceResponse(PlaceResponse):
    """When pulling as a related object, included is always empty
        and links are not in the object"""
    included: dict = {}
    links: dict = Field(..., exclude=True)
