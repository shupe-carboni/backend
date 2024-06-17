from pydantic import BaseModel, Field, create_model
from typing import Optional
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    JSONAPIResponse,
    Pagination,
    Query,
)
from app.jsonapi.sqla_models import (
    SCACustomerLocation,
    SCAPlace,
    # SCAManagerMap,
    # SCAUser,
    ADPAliasToSCACustomerLocation,
    SCACustomer,
    ADPQuote,
)


class LocationResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = SCACustomerLocation.__jsonapi_type_override__


class LocationRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[LocationResourceIdentifier] | LocationResourceIdentifier


## Location
class LocationAttrs(BaseModel):
    hq: bool
    dc: bool


class LocationFilters(BaseModel):
    filter_hq: str = Field(default=None, alias="filter[hq]")
    filter_dc: str = Field(default=None, alias="filter[dc]")


class LocationRelationships(BaseModel):
    customers: JSONAPIRelationships
    places: JSONAPIRelationships
    # users: JSONAPIRelationships = Field(alias=SCAUser.__jsonapi_type_override__)
    # manager_map: JSONAPIRelationships = Field(alias=SCAManagerMap.__jsonapi_type_override__)
    adp_alias_to_sca_customer_locations: Optional[JSONAPIRelationships] = Field(
        default=None, alias=ADPAliasToSCACustomerLocation.__jsonapi_type_override__
    )
    adp_quotes: Optional[JSONAPIRelationships] = Field(
        default=None, alias=ADPQuote.__jsonapi_type_override__
    )


class LocationFields(BaseModel):
    fields_customers: str = Field(default=None, alias="fields[customers]")
    jields_places: str = Field(default=None, alias="fields[places]")
    fields_adp_alias_to_sca_customer_locations: str = Field(
        default=None, alias="fields[adp-alias-to-sca-customer-locations]"
    )
    fields_adp_quotes: str = Field(default=None, alias="fields[adp-quotes]")


class LocationResourceObject(LocationResourceIdentifier):
    attributes: LocationAttrs
    relationships: LocationRelationships


class LocationResponse(JSONAPIResponse):
    data: Optional[list[LocationResourceObject] | LocationResourceObject]


class RelatedLocationResponse(LocationResponse):
    """When pulling as a related object, included is always empty
    and links are not in the object"""

    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_LocationQuery: type[BaseModel] = create_model(
    "LocationQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{f"fields_customer_locations": (Optional[str], None)},
    **{
        f"fields_{field}": (Optional[str], None)
        for field in LocationRelationships.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in LocationAttrs.model_fields.keys()
    },
)


class LocationQuery(_LocationQuery, BaseModel): ...


class LocationQueryJSONAPI(LocationFilters, LocationFields, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class NewLocationRObj(BaseModel):
    type: str = SCACustomerLocation.__jsonapi_type_override__
    attributes: LocationAttrs
    relationships: LocationRelationships


class NewLocation(BaseModel):
    data: NewLocationRObj


class ModLocation(BaseModel):
    data: LocationResourceObject
