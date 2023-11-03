from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth
from app.quotes.models import (
    QuoteResponse,
    QuoteDetailResponse,
    NewQuoteResourceObject,
    NewQuoteDetailResourceObject,
    ExistingQuote,
    ExistingQuoteDetail,
    QuoteQuery 
)

quotes = APIRouter(prefix='/quotes', tags=['quotes'])

@quotes.get('', response_model=QuoteResponse)
async def quotes_collection(
        query: QuoteQuery=Depends(),
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.get('/{quote_id}')
async def quote_detail(
        quote_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> QuoteDetailResponse:
    """
        Rather than just a single quote from the quote collection,
        show more details about the quote like products & accessories with their quantities
    """
    raise HTTPException(status_code=501)

@quotes.delete('/{quote_id}')
async def delete_quote(
        quote_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)) -> None:
    raise HTTPException(status_code=501)

@quotes.post('')
async def new_quote(
        body: NewQuoteResourceObject,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.post('/{quote_id}/products')
async def add_products(
        body: NewQuoteDetailResourceObject,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)) -> QuoteDetailResponse:
    raise HTTPException(status_code=501)

@quotes.patch('/{quote_id}')
async def modify_quote(
        quote_id: int,
        body: ExistingQuote,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)) -> QuoteResponse:
    raise HTTPException(status_code=501)

@quotes.patch('/{quote_id}/products')
async def modify_products(
        quote_id: int,
        body: ExistingQuoteDetail,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)) -> QuoteDetailResponse:
    raise HTTPException(status_code=501)