from pydantic import BaseModel, Field, create_model, ConfigDict
from typing import Optional
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResponse,
    Query,
)

from app.jsonapi.sqla_models import FriedrichCustomer


class FriedrichCustomerRID(JSONAPIResourceIdentifier):
    type: str = FriedrichCustomer.__jsonapi_type_override__


class CudtomerRelResp(JSONAPIRelationshipsResponse):
    data: list[FriedrichCustomerRID] | FriedrichCustomerRID


class FriedrichCustomerAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Optional[str] = Field(default=None, alias="name")
    friedrich_acct_number: Optional[str] = Field(
        default=None, alias="friedrich-acct-number"
    )


class FriedrichCustomerRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    customers: Optional[JSONAPIRelationships] = Field(default=None, alias="customers")
    friedrich_pricing_special: Optional[JSONAPIRelationships] = Field(
        default=None, alias="friedrich-pricing-special"
    )
    friedrich_customers_to_sca_customer_locations: Optional[JSONAPIRelationships] = (
        Field(default=None, alias="friedrich-customers-to-sca-customer-locations")
    )


class FriedrichCustomerFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_name: str = Field(alias="filter[name]")
    filter_friedrich_acct_number: str = Field(alias="filter[friedrich-acct-number]")


class FriedrichCustomerFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_customers: str = Field(alias="fields[customers]")
    fields_friedrich_pricing_special: str = Field(
        alias="fields[friedrich-pricing-special]"
    )
    fields_friedrich_customers_to_sca_customer_locations: str = Field(
        alias="fields[friedrich-customers-to-sca-customer-locations]"
    )
    fields_friedrich_customers: str = Field(alias="fields[friedrich-customers]")


class FriedrichCustomerRObj(FriedrichCustomerRID):
    attributes: FriedrichCustomerAttrs
    relationships: FriedrichCustomerRels


class FriedrichCustomerResp(JSONAPIResponse):
    data: list[FriedrichCustomerRObj] | FriedrichCustomerRObj


class RelatedFriedrichCustomerResp(FriedrichCustomerResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_FriedrichCustomerQuery: type[BaseModel] = create_model(
    "FriedrichCustomerQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in FriedrichCustomerRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in FriedrichCustomerAttrs.model_fields.keys()
    },
    **{
        f"fields_friedrich_customers": (
            Optional[str],
            None,
        )
    },
)


class FriedrichCustomerQuery(_FriedrichCustomerQuery, BaseModel): ...


class FriedrichCustomerQueryJSONAPI(
    FriedrichCustomerFields, FriedrichCustomerFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import FriedrichProduct


class FriedrichProductRID(JSONAPIResourceIdentifier):
    type: str = FriedrichProduct.__jsonapi_type_override__


class CudtomerRelResp(JSONAPIRelationshipsResponse):
    data: list[FriedrichProductRID] | FriedrichProductRID


class FriedrichProductAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    model_number: Optional[str] = Field(default=None, alias="model-number")
    description: Optional[str] = Field(default=None, alias="description")


class FriedrichProductRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    friedrich_pricing: Optional[JSONAPIRelationships] = Field(
        default=None, alias="friedrich-pricing"
    )
    friedrich_pricing_special: Optional[JSONAPIRelationships] = Field(
        default=None, alias="friedrich-pricing-special"
    )


class FriedrichProductFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_model_number: str = Field(alias="filter[model-number]")
    filter_description: str = Field(alias="filter[description]")


class FriedrichProductFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_friedrich_pricing: str = Field(alias="fields[friedrich-pricing]")
    fields_friedrich_pricing_special: str = Field(
        alias="fields[friedrich-pricing-special]"
    )
    fields_friedrich_products: str = Field(alias="fields[friedrich-products]")


class FriedrichProductRObj(FriedrichProductRID):
    attributes: FriedrichProductAttrs
    relationships: FriedrichProductRels


class FriedrichProductResp(JSONAPIResponse):
    data: list[FriedrichProductRObj] | FriedrichProductRObj


class RelatedFriedrichProductResp(FriedrichProductResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_FriedrichProductQuery: type[BaseModel] = create_model(
    "FriedrichProductQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in FriedrichProductRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in FriedrichProductAttrs.model_fields.keys()
    },
    **{
        f"fields_friedrich_products": (
            Optional[str],
            None,
        )
    },
)


class FriedrichProductQuery(_FriedrichProductQuery, BaseModel): ...


class FriedrichProductQueryJSONAPI(
    FriedrichProductFields, FriedrichProductFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import FriedrichPricing
from app.db import FriedrichPriceLevels


class FriedrichPricingRID(JSONAPIResourceIdentifier):
    type: str = FriedrichPricing.__jsonapi_type_override__


class CudtomerRelResp(JSONAPIRelationshipsResponse):
    data: list[FriedrichPricingRID] | FriedrichPricingRID


class FriedrichPricingAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    price_level: Optional[FriedrichPriceLevels] = Field(
        default=None, alias="price-level"
    )
    price: Optional[float] = Field(default=None, alias="price")


class FriedrichPricingRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    friedrich_products: Optional[JSONAPIRelationships] = Field(
        default=None, alias="friedrich-products"
    )


class FriedrichPricingFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_price_level: str = Field(alias="filter[price-level]")
    filter_price: str = Field(alias="filter[price]")


class FriedrichPricingFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_friedrich_products: str = Field(alias="fields[friedrich-products]")
    fields_friedrich_pricing: str = Field(alias="fields[friedrich-pricing]")


class FriedrichPricingRObj(FriedrichPricingRID):
    attributes: FriedrichPricingAttrs
    relationships: FriedrichPricingRels


class FriedrichPricingResp(JSONAPIResponse):
    data: list[FriedrichPricingRObj] | FriedrichPricingRObj


class RelatedFriedrichPricingResp(FriedrichPricingResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_FriedrichPricingQuery: type[BaseModel] = create_model(
    "FriedrichPricingQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in FriedrichPricingRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in FriedrichPricingAttrs.model_fields.keys()
    },
    **{
        f"fields_friedrich_pricing": (
            Optional[str],
            None,
        )
    },
)


class FriedrichPricingQuery(_FriedrichPricingQuery, BaseModel): ...


class FriedrichPricingQueryJSONAPI(
    FriedrichPricingFields, FriedrichPricingFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import FriedrichPricingSpecial


class FriedrichPricingSpecialRID(JSONAPIResourceIdentifier):
    type: str = FriedrichPricingSpecial.__jsonapi_type_override__


class CudtomerRelResp(JSONAPIRelationshipsResponse):
    data: list[FriedrichPricingSpecialRID] | FriedrichPricingSpecialRID


class FriedrichPricingSpecialAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    customer_model_number: Optional[str] = Field(
        default=None, alias="customer-model-number"
    )
    price: Optional[float] = Field(default=None, alias="price")


class FriedrichPricingSpecialRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    friedrich_customers: Optional[JSONAPIRelationships] = Field(
        default=None, alias="friedrich-customers"
    )
    friedrich_products: Optional[JSONAPIRelationships] = Field(
        default=None, alias="friedrich-products"
    )


class FriedrichPricingSpecialFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_customer_model_number: str = Field(alias="filter[customer-model-number]")
    filter_price: str = Field(alias="filter[price]")


class FriedrichPricingSpecialFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_friedrich_customers: str = Field(alias="fields[friedrich-customers]")
    fields_friedrich_products: str = Field(alias="fields[friedrich-products]")
    fields_friedrich_pricing_special: str = Field(
        alias="fields[friedrich-pricing-special]"
    )


class FriedrichPricingSpecialRObj(FriedrichPricingSpecialRID):
    attributes: FriedrichPricingSpecialAttrs
    relationships: FriedrichPricingSpecialRels


class FriedrichPricingSpecialResp(JSONAPIResponse):
    data: list[FriedrichPricingSpecialRObj] | FriedrichPricingSpecialRObj


class RelatedFriedrichPricingSpecialResp(FriedrichPricingSpecialResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_FriedrichPricingSpecialQuery: type[BaseModel] = create_model(
    "FriedrichPricingSpecialQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in FriedrichPricingSpecialRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in FriedrichPricingSpecialAttrs.model_fields.keys()
    },
    **{
        f"fields_friedrich_pricing_special": (
            Optional[str],
            None,
        )
    },
)


class FriedrichPricingSpecialQuery(_FriedrichPricingSpecialQuery, BaseModel): ...


class FriedrichPricingSpecialQueryJSONAPI(
    FriedrichPricingSpecialFields, FriedrichPricingSpecialFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")

from app.jsonapi.sqla_models import FriedrichCustomerPriceLevel


class FriedrichCustomerPriceLevelRID(JSONAPIResourceIdentifier):
    type: str = FriedrichCustomerPriceLevel.__jsonapi_type_override__


class CudtomerRelResp(JSONAPIRelationshipsResponse):
    data: list[FriedrichCustomerPriceLevelRID] | FriedrichCustomerPriceLevelRID


class FriedrichCustomerPriceLevelAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    price_level: Optional[FriedrichPriceLevels] = Field(default=None, alias="price-level")


class FriedrichCustomerPriceLevelRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    friedrich_customers: Optional[JSONAPIRelationships] = Field(default=None, alias="friedrich-customers")


class FriedrichCustomerPriceLevelFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_price_level: str = Field(alias="filter[price-level]")


class FriedrichCustomerPriceLevelFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_friedrich_customers: str = Field(alias="fields[friedrich-customers]")
    fields_friedrich_customer_price_levels: str = Field(alias="fields[friedrich-customer-price-levels]")


class FriedrichCustomerPriceLevelRObj(FriedrichCustomerPriceLevelRID):
    attributes: FriedrichCustomerPriceLevelAttrs
    relationships: FriedrichCustomerPriceLevelRels


class FriedrichCustomerPriceLevelResp(JSONAPIResponse):
    data: list[FriedrichCustomerPriceLevelRObj] | FriedrichCustomerPriceLevelRObj


class RelatedFriedrichCustomerPriceLevelResp(FriedrichCustomerPriceLevelResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_FriedrichCustomerPriceLevelQuery: type[BaseModel] = create_model(
    "FriedrichCustomerPriceLevelQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in FriedrichCustomerPriceLevelRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in FriedrichCustomerPriceLevelAttrs.model_fields.keys()
    },
    **{
        f'fields_friedrich_customer_price_levels': (
            Optional[str],
            None,
        )
    },
)


class FriedrichCustomerPriceLevelQuery(_FriedrichCustomerPriceLevelQuery, BaseModel): ...


class FriedrichCustomerPriceLevelQueryJSONAPI(FriedrichCustomerPriceLevelFields, FriedrichCustomerPriceLevelFilters, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")
