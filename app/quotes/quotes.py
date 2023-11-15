from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth
from app.quotes.models import (
    QuoteResponse,
    NewQuoteResourceObject,
    ExistingQuote,
    QuoteQuery 
)
from app.products.models import ProductResponse, NewProductResourceObject, ExistingProduct

quotes = APIRouter(prefix='/quotes', tags=['quotes'])

@quotes.get('', response_model=QuoteResponse)
async def quote_collection(
        query: QuoteQuery=Depends(),
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.get('/{quote_id}')
async def quote(
        quote_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.delete('/{quote_id}')
async def delete_quote(
        quote_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> None:
    raise HTTPException(status_code=501)

@quotes.delete('/{quote_id}/products/{product_id}')
async def delete_product(
        quote_id: int,
        product_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> None:
    raise HTTPException(status_code=501)


@quotes.post('')
async def new_quote(
        body: NewQuoteResourceObject,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.post('/{quote_id}/products')
async def add_product(
        body: NewProductResourceObject,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> ProductResponse:
    raise HTTPException(status_code=501)

@quotes.patch('/{quote_id}')
async def modify_quote(
        quote_id: int,
        body: ExistingQuote,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.patch('/{quote_id}/products')
async def modify_product(
        quote_id: int,
        body: ExistingProduct,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> ProductResponse:
    raise HTTPException(status_code=501)