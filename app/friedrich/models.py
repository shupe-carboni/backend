from datetime import date, datetime
from pydantic import BaseModel, field_validator
from enum import StrEnum, auto


class QuoteStatus(StrEnum):
    APPROVED = auto()
    DENIED = auto()
    PENDING = auto()
    NEAR_EXPIRED = auto()
    EXPIRED = auto()


STATUS_MAPPING = {
    "Approved": QuoteStatus.APPROVED,
    "Pending Approval": QuoteStatus.PENDING,
    "Approved - About to Expire": QuoteStatus.NEAR_EXPIRED,
}


class QuoteProjectContacts(BaseModel):
    contact_name: str
    contact_email: str
    submitter_name: str
    submitter_email: str


class QuoteProjectAddnlDetails(BaseModel):
    market_type: str
    city: str
    state: str


class QuoteProjectInitalDetails(BaseModel):
    guid: str
    quote_name: str
    account_name: str
    approval_status: QuoteStatus
    quote_number: int
    created_date: date
    expiration_date: date

    @field_validator("created_date", "expiration_date", mode="before")
    @classmethod
    def parse_date(cls, value: str) -> date:
        try:
            return datetime.strptime(value, "%B %d, %Y").date()
        except ValueError as e:
            raise ValueError(
                f"Invalid date format for {value}. Expected Month DD, YYYY"
            ) from e

    @field_validator("approval_status", mode="before")
    @classmethod
    def map_status(cls, value: str) -> QuoteStatus:
        try:
            return STATUS_MAPPING[value]
        except KeyError as e:
            raise KeyError(
                f"Status unmapped for {value}. "
                f"Expected one of the following: {[s for s in QuoteStatus.__members__]}"
            ) from e


class QuoteProjectAttributes(BaseModel):
    quote_name: str
    account_name: str
    approval_status: QuoteStatus
    quote_number: int
    created_date: date
    expiration_date: date
    market_type: str
    city: str
    state: str


class Quote(BaseModel):
    guid: str
    quote_attributes: QuoteProjectAttributes
    quote_contacts: QuoteProjectContacts
