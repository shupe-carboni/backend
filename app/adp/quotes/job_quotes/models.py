from pydantic import BaseModel, Field, create_model
from typing import Optional
from datetime import datetime
from app.jsonapi.core_models import JSONAPIRelationships, JSONAPIResourceObject, Pagination, JSONAPIResourceIdentifier, Query, JSONAPIRelationshipsResponse

class QuoteResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = "adp-quotes"

class QuoteRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[QuoteResourceIdentifier]|QuoteResourceIdentifier

## Unique Quote Information
class QuoteAttributes(BaseModel):
    status: str
    quote_num: str = Field(alias='quote-num')
    job_name: str = Field(alias="job-name")
    date_entered: datetime = Field(alias='date-entered')
    expires: datetime
    quote_document: Optional[str] = Field(None, alias='quote-document')
    plans: Optional[str] = None

    class Config:
        # allows an unpack of the python-dict in snake_case
        populate_by_name = True

class QuoteRelationships(BaseModel):
    sca_place: JSONAPIRelationships
    sca_branch: JSONAPIRelationships
    adp_customer: JSONAPIRelationships 
    adp_quote_products: JSONAPIRelationships

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

