from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth
from app.quotes.job_quotes.models import (
    QuoteResponse,
    NewQuoteResourceObject,
    ExistingQuote,
    QuoteQuery 
)
from app.quotes.products.models import ProductResponse, NewProductResourceObject, ExistingProduct

quotes = APIRouter(prefix='/quotes', tags=['quotes'])

QuotesPerm = Annotated[auth.VerifiedToken, Depends(auth.quotes_perms_present)]

@quotes.get('', response_model=QuoteResponse)
async def quote_collection(
        token: QuotesPerm,
        query: QuoteQuery=Depends(), # type: ignore
    ) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.get('/{quote_id}')
async def quote(
        token: QuotesPerm,
        quote_id: int,
    ) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.delete('/{quote_id}')
async def delete_quote(
        token: QuotesPerm,
        quote_id: int,
    ) -> None:
    raise HTTPException(status_code=501)

@quotes.delete('/{quote_id}/products/{product_id}')
async def delete_product(
        token: QuotesPerm,
        quote_id: int,
        product_id: int,
    ) -> None:
    raise HTTPException(status_code=501)

@quotes.post('')
async def new_quote(
        token: QuotesPerm,
        body: NewQuoteResourceObject,
    ) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.post('/{quote_id}/products')
async def add_product(
        token: QuotesPerm,
    ) -> ProductResponse:
    raise HTTPException(status_code=501)

@quotes.patch('/{quote_id}')
async def modify_quote(
        token: QuotesPerm,
        quote_id: int,
        body: ExistingQuote,
    ) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.patch('/{quote_id}/products')
async def modify_product(
        token: QuotesPerm,
        quote_id: int,
        body: ExistingProduct,
    ) -> ProductResponse:
    raise HTTPException(status_code=501)