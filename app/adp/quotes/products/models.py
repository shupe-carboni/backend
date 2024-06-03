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
    tag: str
    qty: int
    price: Optional[float] = None
    model_number: Optional[str] = Field(default=None, alias="model-number")
    comp_model: Optional[str] = Field(default=None, alias="comp-model")


class ProductQuoteFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_tag: str = Field(default=None, alias="filter[tag]")
    filter_comp_model: Optional[str] = Field(default=None, alias="filter[comp-model]")


# Schema
class ProductRelationships(BaseModel):
    adp_quotes: JSONAPIRelationships = Field(alias="adp-quotes")


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
    id: int


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
