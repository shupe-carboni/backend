from pydantic import BaseModel, Field
from typing import Optional
from app.jsonapi import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    Pagination
)

class ProductResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = "products"

class ProductRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[ProductResourceIdentifier]|ProductResourceIdentifier

## Place
# Schema
## Products & quantities associated with quotes
class ProductAttributes(BaseModel):
    product_tag: Optional[str] = Field(alias="product-tag")
    product_model: Optional[str] = Field(alias="product-model")
    brand: Optional[str]
    qty: int

# Schema
class ProductRelationships(BaseModel):
    quote: JSONAPIRelationships

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
