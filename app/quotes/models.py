from pydantic import BaseModel, Field, create_model
from typing import Optional
from datetime import datetime
from app.jsonapi import JSONAPIRelationships, JSONAPIResourceObject, Pagination, JSONAPIResourceIdentifier, Query

TYPES = {'quotes', 'quotes_products', 'customers', 'locations', 'vendors'} # NOTE replace with dynamic loading from SQLAlchemy Models

## Unique Quote Information
class QuoteAttributes(BaseModel):
    status: str
    quote_num: str = Field(alias='quote-num')
    job_name: str = Field(alias="job-name")
    job_type: str = Field(alias="job-type")
    expires: datetime
    document: str|None

class QuoteRelationships(BaseModel):
    vendor: JSONAPIRelationships
    location: JSONAPIRelationships
    customer: JSONAPIRelationships
    products: JSONAPIRelationships

class QuoteResourceObject(JSONAPIResourceIdentifier):
    attributes: QuoteAttributes
    relationships: QuoteRelationships

class QuoteResponse(BaseModel):
    """High-Level quote details unique by-quote"""
    meta: Optional[dict] = {}
    data: Optional[list[QuoteResourceObject]]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination]



## Products & quantities associated with quotes
class QuoteDetailAttributes(BaseModel):
    product_tag: Optional[str] = Field(alias="product-tag")
    product_model: Optional[str] = Field(alias="product-model")
    brand: Optional[str]
    qty: int

class QuoteDetailRelationships(BaseModel):
    quote: JSONAPIRelationships

class QuoteDetailResourceObject(JSONAPIResourceIdentifier):
    attributes: QuoteDetailAttributes
    relationships: QuoteDetailRelationships

class QuoteDetailResponse(BaseModel):
    """products & accessories with quantities associated with a quote"""
    meta: Optional[dict] = {}
    data: QuoteDetailResourceObject|None


## New Quotes
class NewQuoteResourceObject(BaseModel):
    """new quote request"""
    type: str
    attributes: QuoteAttributes
    relationships: QuoteRelationships
    
class NewQuoteDetailResourceObject(BaseModel):
    """add detail/products to an existing quote"""
    type: str
    attributes: QuoteDetailAttributes
    relationships: QuoteDetailRelationships

## Quote Modifications
class ExistingQuote(NewQuoteResourceObject):
    id: str|int

class ExistingQuoteDetail(NewQuoteDetailResourceObject):
    id: str|int


QuoteQuery = create_model(
    'QuoteQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f"field_{field}":(Optional[str], None) for field in TYPES},
    **{f"filter_{field}":(Optional[str], None) for field in QuoteAttributes.model_fields.keys()},
)

