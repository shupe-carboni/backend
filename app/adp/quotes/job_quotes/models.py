from pydantic import BaseModel, Field, create_model, ConfigDict
from typing import Optional
from datetime import datetime
from app.db import Stage
from app.jsonapi.sqla_models import ADPQuote
from app.jsonapi.core_models import (
    JSONAPIRelationships, JSONAPIResourceObject,
    Pagination, JSONAPIResourceIdentifier,
    Query, JSONAPIRelationshipsResponse
)

class QuoteResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = ADPQuote.__jsonapi_type_override__

class QuoteRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[QuoteResourceIdentifier]|QuoteResourceIdentifier

## Unique Quote Information
class QuoteAttributes(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    adp_quote_id: Optional[str] = Field(default=None, alias='adp-quote-id')
    job_name: str = Field(alias="job-name")
    created_at: datetime = Field(alias='created-at')
    expires_at: datetime = Field(alias='expires-at')
    status: Stage
    quote_doc: Optional[str|bytes] = Field(None, alias='quote-document')
    plans_doc: Optional[str|bytes] = Field(None, alias='plans-document')

class QuoteFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_adp_quote_id: str = Field(default=None, alias='filter[adp-quote-id]')
    filter_job_name: str = Field(default=None, alias='filter[job-name]')
    filter_status: str = Field(default=None, alias='filter[status]')

class QuoteRelationships(BaseModel):
    places: JSONAPIRelationships = None
    customer_locations: JSONAPIRelationships = Field(default=None, alias='customer-locations')
    adp_customers: JSONAPIRelationships  = Field(default=None, alias='adp-customers')
    adp_quote_products: JSONAPIRelationships = Field(default=None, alias='adp-quote-products')

class QuoteFields(BaseModel):
    fields_places: str = Field(default=None, alias='fields[places]')
    fields_customer_locations: str = Field(default=None, alias='fields[customer-locations]')
    fields_adp_customers: str  = Field(default=None, alias='fields[adp-customers]')
    fields_adp_quote_products: str = Field(default=None, alias='fields[adp-quote-products]')

class QuoteResourceObject(JSONAPIResourceIdentifier):
    attributes: QuoteAttributes
    relationships: QuoteRelationships

class QuoteResponse(BaseModel):
    """High-Level quote details unique by-quote"""
    meta: Optional[dict] = {}
    data: Optional[list[QuoteResourceObject] | QuoteResourceObject] = []
    included: Optional[list[JSONAPIResourceObject]] = None
    links: Optional[Pagination] = None

class RelatedQuoteResponse(QuoteResponse):
    """When pulling as a related object, included is always empty
        and links are not in the object"""
    included: dict = {}
    links: dict = Field(default=None, exclude=True)

## New Quotes
class NewQuoteResourceObject(BaseModel):
    """new quote request"""
    type: str
    attributes: QuoteAttributes
    relationships: QuoteRelationships

class NewQuote(BaseModel):
    data: NewQuoteResourceObject

## Quote Modifications
class ExistingQuote(NewQuoteResourceObject):
    id: str|int


# dyanamically created Pydantic Model extends on the non-dyanmic JSON:API Query Model
# by pre-defining and auto-documenting all filter and field square bracket parameters
_QuoteQuery: type[BaseModel] = create_model(
    'QuoteQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f"fields_{field}":(Optional[str], None) for field in QuoteRelationships.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in QuoteAttributes.model_fields.keys()},
)

class QuoteQuery(_QuoteQuery, BaseModel):...
class QuoteQueryJSONAPI(QuoteFilters, QuoteFields, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")