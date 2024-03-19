from pydantic import BaseModel, Field, create_model, ConfigDict
from typing import Optional
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    Pagination,
    Query
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

class PlaceFilters(BaseModel):
    filter_name: str = Field(default=None, alias='filter[name]')
    filter_state: str = Field(default=None, alias='filter[state]')
    filter_lat: str = Field(default=None, alias='filter[lat]')
    filter_long: str = Field(default=None, alias='filter[long]')

# Schema
class PlaceRelationships(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    customer_locations: JSONAPIRelationships = Field(alias='customer-locations')
    adp_quotes: JSONAPIRelationships = Field(alias='adp-quotes')
class PlaceFieldSelector(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    field_customer_locations: str = Field(default=None, alias='fields[customer-locations]')
    field_adp_quotes: str = Field(default=None, alias='fields[adp-quotes]')

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

_PlaceQuery: type[BaseModel] = create_model(
    'PlaceQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f"fields_{field}":(Optional[str], None) for field in PlaceRelationships.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in PlaceAttributes.model_fields.keys()},
)
class PlaceQuery(_PlaceQuery, BaseModel): ...

class PlaceQueryJSONAPI(PlaceFilters, PlaceFieldSelector, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")