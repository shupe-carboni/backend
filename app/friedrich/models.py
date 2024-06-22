from pydantic import BaseModel, Field, create_model, model_validator, ConfigDict
from typing import Optional
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResponse,
    Query,
)
from app.jsonapi.sqla_models import (
    FriedrichCustomer,
    FriedrichCustomertoSCACustomerLocation,
)


class CustomerRID(JSONAPIResourceIdentifier):
    type: str = FriedrichCustomer.__jsonapi_type_override__


class CudtomerRelResp(JSONAPIRelationshipsResponse):
    data: list[CustomerRID] | CustomerRID


class CustomerAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    friedrich_acct_number: str


class CustomerRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    customers: JSONAPIRelationships
    friedrich_customers_to_sca_customer_locations: JSONAPIRelationships = Field(
        alias=FriedrichCustomertoSCACustomerLocation.__jsonapi_type_override__
    )


class CustomerFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_name: str = Field(alias="filter[name]")
    filter_friedrich_acct_number: str = Field(alias="filter[friedrich-acct-number]")


class CustomerFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_customers: str = Field(alias="filter[customers]")
    fields_friedrich_customers_to_sca_customer_locations: str = Field(
        alias="filter[fields-friedrich-customers-to-sca-customer-locations]"
    )
    fields_friedrich_customers: str = Field(alias="fields[friedrich-customers]")


class CustomerRObj(CustomerRID):
    attributes: CustomerAttrs
    relationships: CustomerRels


class CustomerResp(JSONAPIResponse):
    data: list[CustomerRObj] | CustomerRObj


class RelatedCustomerResp(CustomerResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_CustomerQuery: type[BaseModel] = create_model(
    "CustomerQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in CustomerRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in CustomerAttrs.model_fields.keys()
    },
)


class CustomerQuery(_CustomerQuery, BaseModel): ...


class CustomerQueryJSONAPI(CustomerFields, CustomerFilters, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")
