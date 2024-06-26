from pydantic import BaseModel, Field, create_model, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from app.db import Stage
from app.jsonapi.sqla_models import ADPQuote
from app.jsonapi.core_models import (
    JSONAPIRelationships,
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIResponse,
    Query,
)


class QuoteResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = ADPQuote.__jsonapi_type_override__


class QuoteRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[QuoteResourceIdentifier] | QuoteResourceIdentifier


## Unique Quote Information
class QuoteAttributes(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    adp_quote_id: Optional[str] = Field(default=None, alias="adp-quote-id")
    job_name: Optional[str] = Field(default=None, alias="job-name")
    created_at: Optional[datetime] = Field(default=None, alias="created-at")
    expires_at: Optional[datetime] = Field(default=None, alias="expires-at")
    status: Optional[Stage] = Stage.PROPOSED
    quote_doc: Optional[str] = Field(None, alias="quote-doc")
    plans_doc: Optional[str] = Field(None, alias="plans-doc")

    @field_validator("status", mode="before")
    def validate_status(cls, status: str):
        return Stage[status.upper()]


class QuoteFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_adp_quote_id: str = Field(default=None, alias="filter[adp-quote-id]")
    filter_job_name: str = Field(default=None, alias="filter[job-name]")
    filter_status: str = Field(default=None, alias="filter[status]")


class QuoteRelationships(BaseModel):
    places: JSONAPIRelationships = None
    customer_locations: JSONAPIRelationships = Field(
        default=None, alias="customer-locations"
    )
    adp_customers: JSONAPIRelationships = Field(default=None, alias="adp-customers")
    adp_quote_products: JSONAPIRelationships = Field(
        default=None, alias="adp-quote-products"
    )


class QuoteFields(BaseModel):
    fields_adp_quotes: str = Field(default=None, alias="fields[adp-quotes]")
    fields_places: str = Field(default=None, alias="fields[places]")
    fields_customer_locations: str = Field(
        default=None, alias="fields[customer-locations]"
    )
    fields_adp_customers: str = Field(default=None, alias="fields[adp-customers]")
    fields_adp_quote_products: str = Field(
        default=None, alias="fields[adp-quote-products]"
    )


class QuoteResourceObject(JSONAPIResourceIdentifier):
    attributes: QuoteAttributes
    relationships: QuoteRelationships


class QuoteResponse(JSONAPIResponse):
    """High-Level quote details unique by-quote"""

    data: Optional[list[QuoteResourceObject] | QuoteResourceObject] = []


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
    id: str | int


class ExistingQuoteRequest(BaseModel):
    data: ExistingQuote


# dyanamically created Pydantic Model extends on the non-dyanmic JSON:API Query Model
# by pre-defining and auto-documenting all filter and field square bracket parameters
_QuoteQuery: type[BaseModel] = create_model(
    "QuoteQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in QuoteRelationships.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in QuoteAttributes.model_fields.keys()
    },
    **{
        f"fields_{ADPQuote.__tablename__}": (
            Optional[str],
            None,
        )
    },
)


class QuoteQuery(_QuoteQuery, BaseModel): ...


class QuoteQueryJSONAPI(QuoteFilters, QuoteFields, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")
