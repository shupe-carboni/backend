from pydantic import BaseModel, Field
from typing import Optional
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    Pagination,
)
from app.jsonapi.sqla_models import (
    SCACustomerLocation,
    SCAPlace,
    # SCAManagerMap,
    # SCAUser,
    # ADPAliasToSCACustomerLocation,
    SCACustomer,
    ADPQuote,
)


class LocationResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = SCACustomerLocation.__jsonapi_type_override__


class LocationRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[LocationResourceIdentifier] | LocationResourceIdentifier


## Location
# Schema
class LocationAttrs(BaseModel):
    hq: bool
    dc: bool


class LocationRelationships(BaseModel):
    customers: JSONAPIRelationships = Field(alias=SCACustomer.__jsonapi_type_override__)
    places: JSONAPIRelationships = Field(alias=SCAPlace.__jsonapi_type_override__)
    # users: JSONAPIRelationships = Field(alias=SCAUser.__jsonapi_type_override__)
    # manager_map: JSONAPIRelationships = Field(alias=SCAManagerMap.__jsonapi_type_override__)
    # adp_alias_to_sca_customer_locations
    adp_quotes: JSONAPIRelationships = Field(alias=ADPQuote.__jsonapi_type_override__)


class LocationResourceObject(LocationResourceIdentifier):
    attributes: LocationAttrs
    relationships: LocationRelationships


class LocationResponse(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[LocationResourceObject] | LocationResourceObject]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination]


class RelatedLocationResponse(LocationResponse):
    """When pulling as a related object, included is always empty
    and links are not in the object"""

    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)
