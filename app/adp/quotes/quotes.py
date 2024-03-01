from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import ADP_DB
from app.adp.quotes.job_quotes.models import (
    QuoteResponse,
    NewQuoteResourceObject,
    ExistingQuote,
    QuoteQuery 
)
from app.adp.quotes.products.models import ProductResponse, NewProductResourceObject, ExistingProduct

quotes = APIRouter(prefix='/quotes', tags=['quotes'])

ADPQuotesPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_quotes_perms)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]

@quotes.get('', response_model=QuoteResponse)
async def quote_collection(
        token: ADPQuotesPerm,
        session: NewSession,
        query: QuoteQuery=Depends(), # type: ignore
    ) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.get('/{quote_id}')
async def quote(
        token: ADPQuotesPerm,
        quote_id: int,
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

@quotes.delete('/{quote_id}/products/{product_id}')
async def delete_product(
        token: ADPQuotesPerm,
        quote_id: int,
        product_id: int,
        session: NewSession,
    ) -> None:
    raise HTTPException(status_code=501)

@quotes.post('')
async def new_quote(
        token: ADPQuotesPerm,
        body: NewQuoteResourceObject,
        session: NewSession,
    ) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.post('/{quote_id}/products')
async def add_product(
        token: ADPQuotesPerm,
        session: NewSession,
    ) -> ProductResponse:
    raise HTTPException(status_code=501)

@quotes.patch('/{quote_id}')
async def modify_quote(
        token: ADPQuotesPerm,
        quote_id: int,
        body: ExistingQuote,
        session: NewSession,
    ) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.patch('/{quote_id}/products')
async def modify_product(
        token: ADPQuotesPerm,
        quote_id: int,
        body: ExistingProduct,
        session: NewSession,
    ) -> ProductResponse:
    raise HTTPException(status_code=501)