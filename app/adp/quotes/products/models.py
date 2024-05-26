from pydantic import BaseModel, Field, ConfigDict, create_model
from typing import Optional
from app.jsonapi.sqla_models import ADPQuoteProduct
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    Pagination,
    Query,
)


class ProductResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = ADPQuoteProduct.__jsonapi_type_override__


class ProductRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[ProductResourceIdentifier] | ProductResourceIdentifier


## Products & quantities associated with quotes
# Schema
class ProductAttributes(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    request_brand: Optional[str] = Field(default=None, alias="request-brand")
    product_tag_or_model: str = Field(alias="product-tag-or-model")
    product_model_quoted: Optional[str] = Field(
        default=None, alias="product-model-quoted"
    )
    qty: int
    price: Optional[float] = None


class ProductQuoteFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_product_tag_or_model: str = Field(
        default=None, alias="filter[product-tag-or-model]"
    )
    filter_product_model_quoted: Optional[str] = Field(
        default=None, alias="filter[product-model-quoted]"
    )


# Schema
class ProductRelationships(BaseModel):
    adp_quotes: JSONAPIRelationships


class ProductQuoteFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_adp_quotes: str = Field(default=None, alias="fields[adp-quotes]")


class ProductResourceObject(ProductResourceIdentifier):
    attributes: ProductAttributes
    relationships: ProductRelationships


class ProductResponse(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[ProductResourceObject] | ProductResourceObject]
    included: Optional[list[JSONAPIResourceObject]] = []
    links: Optional[Pagination] = None


class NewProductResourceObject(BaseModel):
    """add detail/products to an existing quote"""

    type: str
    attributes: ProductAttributes
    relationships: ProductRelationships


class ExistingProduct(NewProductResourceObject):
    id: str | int


class RelatedProductResponse(ProductResponse):
    """When pulling as a related object, included is always empty
    and links are not in the object"""

    included: dict = {}
    links: dict = Field(default=None, exclude=True)


# dyanamically created Pydantic Model extends on the non-dyanmic JSON:API Query Model
# by pre-defining and auto-documenting all filter and field square bracket parameters
_QuoteProductQuery: type[BaseModel] = create_model(
    "QuoteQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in ProductRelationships.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in ProductAttributes.model_fields.keys()
    },
)


class QuoteProductQuery(_QuoteProductQuery, BaseModel): ...


class QuoteQueryJSONAPI(ProductQuoteFilters, ProductQuoteFields, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")
