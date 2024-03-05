from pydantic import BaseModel, Field
from typing import Optional
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    Pagination
)

class ProductResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = "quote_products"

class ProductRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[ProductResourceIdentifier]|ProductResourceIdentifier

## Products & quantities associated with quotes
# Schema
class ProductAttributes(BaseModel):
    request_brand: Optional[str] = Field(alias='request-brand')
    product_tag_or_model: str = Field(alias="product-tag-or-model")
    product_model_quoted: Optional[str] = Field(alias="product-model-quoted")
    qty: int
    price: Optional[float] = None
    class Config:
        populate_by_name = True

# Schema
class ProductRelationships(BaseModel):
    adp_quote: JSONAPIRelationships

class ProductResourceObject(ProductResourceIdentifier):
    attributes: ProductAttributes
    relationships: ProductRelationships

class ProductResponse(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[ProductResourceObject]]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination]

class NewProductResourceObject(BaseModel):
    """add detail/products to an existing quote"""
    type: str
    attributes: ProductAttributes
    relationships: ProductRelationships

class ExistingProduct(NewProductResourceObject):
    id: str|int

class RelatedProductResponse(ProductResponse):
    """When pulling as a related object, included is always empty
        and links are not in the object"""
    included: dict = {}
    links: dict = Field(..., exclude=True)
