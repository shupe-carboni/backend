"""Locations, in consistency with commissions data, designates a city, state
    lat, long, and id (from GeoNames) to either a customer's branch OR the locale
    of a quoted job"""

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
class LocationAttrs(BaseModel):
    city: str
    state: str
    lat: float
    long: float
class LocationRelationships(BaseModel):
    branches: JSONAPIRelationships
    quotes: JSONAPIRelationships

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
    links: dict = Field(..., exclude=True)