from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.jsonapi import JSONAPIRelationships, JSONAPIResourceObject, Pagination, JSONAPIResourceIdentifier

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
    type: str
    attributes: QuoteAttributes
    relationships: QuoteRelationships
    
class NewQuoteDetailResourceObject(BaseModel):
    type: str
    attributes: QuoteDetailAttributes
    relationships: QuoteDetailRelationships

class NewQuoteRequest(BaseModel):
    """Create either the new high-level quote or
    the associated products & accessories with an existing quote"""
    data: NewQuoteResourceObject|NewQuoteDetailResourceObject