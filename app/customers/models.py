from pydantic import BaseModel, Field, create_model, ConfigDict, StringConstraints
from typing import Optional, Annotated
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResponse,
    Query,
)
from app.jsonapi.sqla_models import SCACustomer


class CustomerResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = SCACustomer.__jsonapi_type_override__


class CustomerRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[CustomerResourceIdentifier] | CustomerResourceIdentifier


## Customers
# Schema
class CustomerAttributes(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Annotated[
        Optional[str], StringConstraints(to_upper=True, strip_whitespace=True)
    ] = None
    domains: Optional[list[str]] = None
    logo: Optional[str] = None
    buying_group: Optional[str] = Field(default=None, alias="buying-group")


class CustomerFilterSelector(BaseModel):
    filter_name: str = Field(default=None, alias="filter[name]")
    filter_domains: str = Field(default=None, alias="filter[domains]")
    filter_logo: str = Field(default=None, alias="filter[logo]")
    filter_buying_group: str = Field(default=None, alias="filter[buying-group]")


# Schema
class CustomerRelationships(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    customer_locations: JSONAPIRelationships = Field(alias="customer-locations")


class CustomerRelationshipsFieldsSelectors(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_customer_locations: str = Field(
        default=None, alias="fields[customer-locations]"
    )
    fields_adp_customers: str = Field(default=None, alias="fields[adp-customers]")
    fields_adp_customer_terms: str = Field(
        default=None, alias="fields[adp-customer-terms]"
    )


class CustomerResourceObject(CustomerResourceIdentifier):
    attributes: CustomerAttributes
    relationships: CustomerRelationships


class CustomerResponse(JSONAPIResponse):
    data: Optional[list[CustomerResourceObject] | CustomerResourceObject]


class RelatedCustomerResponse(CustomerResponse):
    """When pulling as a related object, included is always empty
    and links are not in the object"""

    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_CustomerQuery: type[BaseModel] = create_model(
    "CustomerQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{f"fields_customers": (Optional[str], None)},
    **{
        f"fields_{field}": (Optional[str], None)
        for field in CustomerRelationships.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in CustomerAttributes.model_fields.keys()
    },
)


class CustomerQuery(_CustomerQuery, BaseModel): ...


class CustomerQueryJSONAPI(
    CustomerFilterSelector, CustomerRelationshipsFieldsSelectors, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class NewCustomerRObj(BaseModel):
    id: Optional[int] = None
    type: str = SCACustomer.__jsonapi_type_override__
    attributes: CustomerAttributes


class NewCustomer(BaseModel):
    data: NewCustomerRObj


class CustomerModLogoAttr(BaseModel):
    logo: str


class ModCustomerRObj(BaseModel):
    id: int
    type: str = SCACustomer.__jsonapi_type_override__
    attributes: CustomerAttributes | CustomerModLogoAttr
    relationships: CustomerRelationships | dict = {}


class ModCustomer(BaseModel):
    data: ModCustomerRObj


## CMMSSNS Customer
class CMMSSNSCustomerSearchResult(BaseModel):
    id: int
    name: str


class CMMSSNSCustomerResults(BaseModel):
    data: list[CMMSSNSCustomerSearchResult]


class NewCMMSSNSCustomerAttrs(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str


class NewCMMSSNSCustomerObj(BaseModel):
    type: str = "customers"
    attributes: NewCMMSSNSCustomerAttrs


class NewCMMSSNSCustomerObjwID(NewCMMSSNSCustomerObj):
    id: int


class NewCMMSSNSCustomer(BaseModel):
    data: NewCMMSSNSCustomerObj


class CMMSSNSCustomerResp(BaseModel):
    jsonapi: dict[str, str]
    meta: dict[str, str]
    included: list = []
    data: NewCMMSSNSCustomerObjwID
