from pydantic import BaseModel, Field, create_model
from typing import Optional
from datetime import datetime
from app.jsonapi import JSONAPIRelationships, JSONAPIResourceObject, Pagination, JSONAPIResourceIdentifier, Query, JSONAPIRelationshipsResponse

class QuoteResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = "quotes"

class QuoteRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[QuoteResourceIdentifier]|QuoteResourceIdentifier

## Unique Quote Information
class QuoteAttributes(BaseModel):
    status: str
    quote_num: str = Field(alias='quote-num')
    job_name: str = Field(alias="job-name")
    job_type: str = Field(alias="job-type")
    expires: datetime
    document: str|None

    class Config:
        # allows an unpack of the python-dict in snake_case
        populate_by_name = True

class QuoteRelationships(BaseModel):
    vendor: JSONAPIRelationships
    place: JSONAPIRelationships
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

class RelatedQuoteResponse(QuoteResponse):
    """When pulling as a related object, included is always empty
        and links are not in the object"""
    included: dict = {}
    links: dict = Field(..., exclude=True)

## New Quotes
class NewQuoteResourceObject(BaseModel):
    """new quote request"""
    type: str
    attributes: QuoteAttributes
    relationships: QuoteRelationships
    
## Quote Modifications
class ExistingQuote(NewQuoteResourceObject):
    id: str|int



# dyanamically created Pydantic Model extends on the non-dyanmic JSON:API Query Model
# by pre-defining and auto-documenting all filter and field square bracket parameters
QuoteQuery: type[BaseModel] = create_model(
    'QuoteQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f"fields_{field}":(Optional[str], None) for field in QuoteRelationships.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in QuoteAttributes.model_fields.keys()},
)

