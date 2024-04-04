from io import BytesIO
from typing import Annotated
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, Form, UploadFile
from fastapi.routing import APIRouter
from app import auth
from app.db import ADP_DB, Stage
from app.jsonapi.core_models import convert_query
from app.adp.quotes.job_quotes.models import (
    QuoteResponse, NewQuote,
    ExistingQuote, QuoteQuery, QuoteQueryJSONAPI 
)
from app.jsonapi.sqla_models import ADPQuote

QUOTES_RESOURCE = ADPQuote.__jsonapi_type_override__
quotes = APIRouter(prefix=f'/{QUOTES_RESOURCE}', tags=['adp quotes'])

ADPQuotesPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_quotes_perms)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(QuoteQueryJSONAPI)

@dataclass
class NewFile:
    file_name: str
    file_mime: str
    file_content: bytes|BytesIO


@quotes.get('', response_model=QuoteResponse, response_model_exclude_none=True)
async def quote_collection(
        token: ADPQuotesPerm,
        session: NewSession,
        query: QuoteQuery=Depends()
    ) -> QuoteResponse:
    """Look at all quotes.
        SCA employees (>= sca_employee) will see all quotes,
        customers (>=customer_std) will see only quotes associated with them"""
    return auth.secured_get_query(
        db=ADP_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['quotes'],
        resource=QUOTES_RESOURCE,
        query=converter(query)
    )

@quotes.get('/{quote_id}', response_model=QuoteResponse, response_model_exclude_none=True)
async def one_quote(
        token: ADPQuotesPerm,
        quote_id: int,
        session: NewSession,
        query: QuoteQuery=Depends()
    ) -> QuoteResponse:
    """Look a single quote.
        SCA employees (>= sca_employee) can view any quote
        customers (>=customer_std) can view only quotes associated with them"""
    return auth.secured_get_query(
        db=ADP_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['quotes'],
        resource=QUOTES_RESOURCE,
        query=converter(query),
        obj_id=quote_id
    )

@quotes.post('', response_model=QuoteResponse, response_model_exclude_none=True)
async def new_quote(
        token: ADPQuotesPerm,
        session: NewSession,
        quote_doc: UploadFile,
        plans_doc: UploadFile,
        adp_quote_id: str = Form(defualt=None),
        job_name: str = Form(),
        expires_at: datetime = Form(),
        status: Stage = Form(),
        place_id: int = Form(),
        customer_location_id: int = Form(),
        adp_customer_id: int = Form()
    ) -> QuoteResponse:
    """Create a new quote.
        - Quote ID, quote documents and plan documents are not required for creation.
        - Create timestamp ought to generated client-side and sent with the request, whereas
        - Expiration date is determined by rules associated with quote creation (i.e. +90 days).
        - Stage should defualt to 'proposed', but ought to be selectable."""
    # TODO generate filenames and upload documents to S3. Plug the links to them into a NewQuote before post_collection
    created_at: datetime = datetime.today().date()
    if token.permissions.get('quotes') >= auth.QuotePermPriority.sca_employee:
        # do it
        new_quote_obj = {
            "type": QUOTES_RESOURCE,
            "attributes": {
                ''
            }
        }
        raise HTTPException(status_code=501)
    raise HTTPException(status_code=401)

@quotes.patch('/{quote_id}', response_model=QuoteResponse, response_model_exclude_none=True)
async def modify_quote(
        token: ADPQuotesPerm,
        quote_id: int,
        body: ExistingQuote,
        session: NewSession,
    ) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.delete('/{quote_id}')
async def delete_quote(
        token: ADPQuotesPerm,
        quote_id: int,
        session: NewSession,
    ) -> None:
    raise HTTPException(status_code=501)
