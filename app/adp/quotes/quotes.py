from io import BytesIO
from typing import Annotated, Optional
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
S3_DIR = '/adp/quotes/'
quotes = APIRouter(prefix=f'/{QUOTES_RESOURCE}', tags=['adp quotes'])

ADPQuotesPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_quotes_perms)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(QuoteQueryJSONAPI)

@dataclass
class NewFile:
    file_name: str
    file_mime: str
    file_content: bytes|BytesIO
    def __post_init__(self) -> None:
        self.s3 = S3_DIR

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
        adp_quote_id: str = Form(defualt=None),
        job_name: str = Form(),
        expires_at: datetime = Form(),
        status: Stage = Form(),
        quote_doc: Optional[UploadFile]=None,
        plans_doc: Optional[UploadFile]=None,
        place_id: int = Form(),
        customer_location_id: int = Form(),
        adp_customer_id: int = Form()
    ) -> QuoteResponse:
    """Create a new quote.
        - ADP Quote ID, quote documents and plan documents are not required for creation.
        - ADP Quote ID comes from ADP and ought to be added in later if not supplied on creation.
        - Create timestamp is auto-generated and stuffed into the JSONAPI request
        - Expiration date is determined by rules associated with quote creation (i.e. +90 days).
        - Stage should defualt to 'proposed', but ought to be selectable."""
    # TODO generate filenames and upload documents to S3. Plug the links to them into a NewQuote before post_collection
    created_at: datetime = datetime.today().date()
    if token.permissions.get('quotes') >= auth.QuotePermPriority.sca_employee:
        attrs = {
            'job_name': job_name,
            'created_at': created_at,
            'expires_at': expires_at,
            'staus': status,
        }
        if adp_quote_id:
            attrs['adp_quote_id'] = adp_quote_id
        if quote_doc:
            quote_file = NewFile(
                file_name=S3_DIR+quote_doc.filename,
                file_mime=quote_doc.content_type,
                file_content=await quote_doc.read()
            )
            # TODO do the upload to AWS
            attrs['quote_doc'] = quote_file.s3

        if plans_doc:
            plans_file = NewFile(
                file_name=S3_DIR+plans_doc.filename,
                file_mime=plans_doc.content_type,
                file_content=await plans_doc.read()
            )
            # TODO do the upload to AWS
            attrs['plans_doc'] = plans_file.s3

        new_quote_obj = {
            "type": QUOTES_RESOURCE,
            "attributes": attrs,
            "relationships": {
                'places': {
                    'data': {
                        'id': place_id,
                        'type': 'places'
                    }
                },
                'customer-locations': {
                    'data': {
                        'id': customer_location_id,
                        'type': 'customer-locations'
                    }
                },
                'adp-customers': {
                    'data': {
                        'id': adp_customer_id,
                        'type': 'adp-customers'
                    }
                },
            }
        }
        new_quote = NewQuote(data=new_quote_obj)
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
