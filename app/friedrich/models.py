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
from app.db import FriedrichPriceLevels


class FriedrichCustomerRID(JSONAPIResourceIdentifier):
    type: str = FriedrichCustomer.__jsonapi_type_override__


class FriedrichCustomerRelResp(JSONAPIRelationshipsResponse):
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
    friedrich_customer_price_levels: Optional[JSONAPIRelationships] = Field(
        default=None, alias="friedrich-customer-price-levels"
    )


class FriedrichCustomerFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_name: str = Field(default=None, alias="filter[name]")
    filter_friedrich_acct_number: str = Field(
        default=None, alias="filter[friedrich-acct-number]"
    )


class FriedrichCustomerFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_customers: str = Field(default=None, alias="fields[customers]")
    fields_friedrich_pricing_special: str = Field(
        default=None, alias="fields[friedrich-pricing-special]"
    )
    fields_friedrich_customers_to_sca_customer_locations: str = Field(
        default=None, alias="fields[friedrich-customers-to-sca-customer-locations]"
    )
    fields_friedrich_customer_price_levels: str = Field(
        default=None, alias="fields[friedrich-customer-price-levels]"
    )
    fields_friedrich_customers: str = Field(
        default=None, alias="fields[friedrich-customers]"
    )


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


class ModFriedrichCustomerAttrs(BaseModel):
    name: Optional[str] = Field(default=None, alias="name")
    friedrich_acct_number: Optional[str] = Field(
        default=None, alias="friedrich-acct-number"
    )


class ModFriedrichCustomerRObj(BaseModel):
    id: int
    type: str = FriedrichCustomer.__jsonapi_type_override__
    attributes: ModFriedrichCustomerAttrs
    relationships: FriedrichCustomerRels


class ModFriedrichCustomer(BaseModel):
    data: ModFriedrichCustomerRObj


from app.jsonapi.sqla_models import FriedrichPricing


class FriedrichPricingRID(JSONAPIResourceIdentifier):
    type: str = FriedrichPricing.__jsonapi_type_override__


class FriedrichPricingRelResp(JSONAPIRelationshipsResponse):
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
    filter_price_level: str = Field(default=None, alias="filter[price-level]")
    filter_price: str = Field(default=None, alias="filter[price]")


class FriedrichPricingFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_friedrich_products: str = Field(
        default=None, alias="fields[friedrich-products]"
    )
    fields_friedrich_pricing: str = Field(
        default=None, alias="fields[friedrich-pricing]"
    )


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


class ModFriedrichPricingAttrs(BaseModel):
    price: Optional[float] = Field(default=None, alias="price")


class ModFriedrichPricingRObj(BaseModel):
    id: int
    type: str = FriedrichPricing.__jsonapi_type_override__
    attributes: ModFriedrichPricingAttrs
    relationships: FriedrichPricingRels


class ModFriedrichPricing(BaseModel):
    data: ModFriedrichPricingRObj


from app.jsonapi.sqla_models import FriedrichPricingSpecial


class FriedrichPricingSpecialRID(JSONAPIResourceIdentifier):
    type: str = FriedrichPricingSpecial.__jsonapi_type_override__


class FriedrichPricingSpecialRelResp(JSONAPIRelationshipsResponse):
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
    filter_customer_model_number: str = Field(
        default=None, alias="filter[customer-model-number]"
    )
    filter_price: str = Field(default=None, alias="filter[price]")


class FriedrichPricingSpecialFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_friedrich_customers: str = Field(
        default=None, alias="fields[friedrich-customers]"
    )
    fields_friedrich_products: str = Field(
        default=None, alias="fields[friedrich-products]"
    )
    fields_friedrich_pricing_special: str = Field(
        default=None, alias="fields[friedrich-pricing-special]"
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


class ModFriedrichPricingSpecialAttrs(BaseModel):
    customer_model_number: Optional[str] = Field(
        default=None, alias="customer-model-number"
    )
    price: Optional[float] = Field(default=None, alias="price")


class ModFriedrichPricingSpecialRObj(BaseModel):
    id: int
    type: str = FriedrichPricingSpecial.__jsonapi_type_override__
    attributes: ModFriedrichPricingSpecialAttrs
    relationships: FriedrichPricingSpecialRels


class ModFriedrichPricingSpecial(BaseModel):
    data: ModFriedrichPricingSpecialRObj


from app.jsonapi.sqla_models import FriedrichCustomerPriceLevel


class FriedrichCustomerPriceLevelRID(JSONAPIResourceIdentifier):
    type: str = FriedrichCustomerPriceLevel.__jsonapi_type_override__


class FriedrichCustomerPriceLevelRelResp(JSONAPIRelationshipsResponse):
    data: list[FriedrichCustomerPriceLevelRID] | FriedrichCustomerPriceLevelRID


class FriedrichCustomerPriceLevelAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    price_level: Optional[FriedrichPriceLevels] = Field(
        default=None, alias="price-level"
    )


class FriedrichCustomerPriceLevelRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    friedrich_customers: Optional[JSONAPIRelationships] = Field(
        default=None, alias="friedrich-customers"
    )


class FriedrichCustomerPriceLevelFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_price_level: str = Field(default=None, alias="filter[price-level]")


class FriedrichCustomerPriceLevelFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_friedrich_customers: str = Field(
        default=None, alias="fields[friedrich-customers]"
    )
    fields_friedrich_customer_price_levels: str = Field(
        default=None, alias="fields[friedrich-customer-price-levels]"
    )


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
        f"fields_friedrich_customer_price_levels": (
            Optional[str],
            None,
        )
    },
)


class FriedrichCustomerPriceLevelQuery(
    _FriedrichCustomerPriceLevelQuery, BaseModel
): ...


class FriedrichCustomerPriceLevelQueryJSONAPI(
    FriedrichCustomerPriceLevelFields, FriedrichCustomerPriceLevelFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModFriedrichCustomerPriceLevelAttrs(BaseModel):
    price_level: Optional[FriedrichPriceLevels] = Field(
        default=None, alias="price-level"
    )


class ModFriedrichCustomerPriceLevelRObj(BaseModel):
    id: int
    type: str = FriedrichCustomerPriceLevel.__jsonapi_type_override__
    attributes: ModFriedrichCustomerPriceLevelAttrs
    relationships: FriedrichCustomerPriceLevelRels


class ModFriedrichCustomerPriceLevel(BaseModel):
    data: ModFriedrichCustomerPriceLevelRObj


from app.jsonapi.sqla_models import FriedrichProduct


class FriedrichProductRID(JSONAPIResourceIdentifier):
    type: str = FriedrichProduct.__jsonapi_type_override__


class FriedrichProductRelResp(JSONAPIRelationshipsResponse):
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
    filter_model_number: str = Field(default=None, alias="filter[model-number]")
    filter_description: str = Field(default=None, alias="filter[description]")


class FriedrichProductFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_friedrich_pricing: str = Field(
        default=None, alias="fields[friedrich-pricing]"
    )
    fields_friedrich_pricing_special: str = Field(
        default=None, alias="fields[friedrich-pricing-special]"
    )
    fields_friedrich_products: str = Field(
        default=None, alias="fields[friedrich-products]"
    )


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
    include: Optional[str] = Field(default=None, exclude=True)
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModFriedrichProductAttrs(BaseModel):
    description: Optional[str] = Field(default=None, alias="description")


class ModFriedrichProductRObj(BaseModel):
    id: int
    type: str = FriedrichProduct.__jsonapi_type_override__
    attributes: ModFriedrichProductAttrs
    relationships: FriedrichProductRels


class ModFriedrichProduct(BaseModel):
    data: ModFriedrichProductRObj


from app.jsonapi.sqla_models import FriedrichPricingCustomer


class FriedrichPricingCustomerRID(JSONAPIResourceIdentifier):
    type: str = FriedrichPricingCustomer.__jsonapi_type_override__


class FriedrichPricingCustomerRelResp(JSONAPIRelationshipsResponse):
    data: list[FriedrichPricingCustomerRID] | FriedrichPricingCustomerRID


class FriedrichPricingCustomerAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class FriedrichPricingCustomerRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    friedrich_customers: Optional[JSONAPIRelationships] = Field(
        default=None, alias="friedrich-customers"
    )
    friedrich_pricing: Optional[JSONAPIRelationships] = Field(
        default=None, alias="friedrich-pricing"
    )


class FriedrichPricingCustomerFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class FriedrichPricingCustomerFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_friedrich_customers: str = Field(
        default=None, alias="fields[friedrich-customers]"
    )
    fields_friedrich_pricing: str = Field(
        default=None, alias="fields[friedrich-pricing]"
    )
    fields_friedrich_pricing_customers: str = Field(
        default=None, alias="fields[friedrich-pricing-customers]"
    )


class FriedrichPricingCustomerRObj(FriedrichPricingCustomerRID):
    attributes: FriedrichPricingCustomerAttrs
    relationships: FriedrichPricingCustomerRels


class FriedrichPricingCustomerResp(JSONAPIResponse):
    data: list[FriedrichPricingCustomerRObj] | FriedrichPricingCustomerRObj


class RelatedFriedrichPricingCustomerResp(FriedrichPricingCustomerResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_FriedrichPricingCustomerQuery: type[BaseModel] = create_model(
    "FriedrichPricingCustomerQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in FriedrichPricingCustomerRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in FriedrichPricingCustomerAttrs.model_fields.keys()
    },
    **{
        f"fields_friedrich_pricing_customers": (
            Optional[str],
            None,
        )
    },
)


class FriedrichPricingCustomerQuery(_FriedrichPricingCustomerQuery, BaseModel): ...


class FriedrichPricingCustomerQueryJSONAPI(
    FriedrichPricingCustomerFields, FriedrichPricingCustomerFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import FriedrichPricingSpecialCustomer


class FriedrichPricingSpecialCustomerRID(JSONAPIResourceIdentifier):
    type: str = FriedrichPricingSpecialCustomer.__jsonapi_type_override__


class FriedrichPricingSpecialCustomerRelResp(JSONAPIRelationshipsResponse):
    data: list[FriedrichPricingSpecialCustomerRID] | FriedrichPricingSpecialCustomerRID


class FriedrichPricingSpecialCustomerAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class FriedrichPricingSpecialCustomerRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    friedrich_customers: Optional[JSONAPIRelationships] = Field(
        default=None, alias="friedrich-customers"
    )
    friedrich_pricing_special: Optional[JSONAPIRelationships] = Field(
        default=None, alias="friedrich-pricing-special"
    )


class FriedrichPricingSpecialCustomerFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class FriedrichPricingSpecialCustomerFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_friedrich_customers: str = Field(
        default=None, alias="fields[friedrich-customers]"
    )
    fields_friedrich_pricing_special: str = Field(
        default=None, alias="fields[friedrich-pricing-special]"
    )
    fields_friedrich_pricing_special_customers: str = Field(
        default=None, alias="fields[friedrich-pricing-special-customers]"
    )


class FriedrichPricingSpecialCustomerRObj(FriedrichPricingSpecialCustomerRID):
    attributes: FriedrichPricingSpecialCustomerAttrs
    relationships: FriedrichPricingSpecialCustomerRels


class FriedrichPricingSpecialCustomerResp(JSONAPIResponse):
    data: (
        list[FriedrichPricingSpecialCustomerRObj] | FriedrichPricingSpecialCustomerRObj
    )


class RelatedFriedrichPricingSpecialCustomerResp(FriedrichPricingSpecialCustomerResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_FriedrichPricingSpecialCustomerQuery: type[BaseModel] = create_model(
    "FriedrichPricingSpecialCustomerQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in FriedrichPricingSpecialCustomerRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in FriedrichPricingSpecialCustomerAttrs.model_fields.keys()
    },
    **{
        f"fields_friedrich_pricing_special_customers": (
            Optional[str],
            None,
        )
    },
)


class FriedrichPricingSpecialCustomerQuery(
    _FriedrichPricingSpecialCustomerQuery, BaseModel
): ...


class FriedrichPricingSpecialCustomerQueryJSONAPI(
    FriedrichPricingSpecialCustomerFields, FriedrichPricingSpecialCustomerFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")
