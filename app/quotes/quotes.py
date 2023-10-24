from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app.quotes.models import (
    QuoteResponse,
    QuoteDetailResponse,
    NewQuoteRequest,
    NewQuoteResourceObject,
    NewQuoteDetailResourceObject,
    ExistingQuoteRequest,
    ExistingQuote,
    ExistingQuoteDetail
)
from app.jsonapi import Query
from app import auth

quotes = APIRouter(prefix='/quotes', tags=['quotes'])

@quotes.get('', response_model=QuoteResponse)
async def quotes_collection(
        query: Query=Depends(),
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> QuoteResponse:
    responses = {
        -1: 'none',
        0: 'lowest',
        1: 'going up',
        2: 'a little higher',
        3: 'the tippy top'
    }
    response = responses[token.perm_level('quotes')]
    raise HTTPException(status_code=501, detail=response)

@quotes.get('/{quote_id}')
async def quote_detail(
        quote_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> QuoteDetailResponse:
    """
        Rather than just a single quote from the quote collection,
        show more details about the quote like products & accessories with their quantities
    """
    print(quote_id)
    raise HTTPException(status_code=501)

@quotes.delete('/{quote_id}')
async def delete_quote(quote_id: int) -> None:
    print(quote_id)
    raise HTTPException(status_code=501)

@quotes.post('')
async def new_quote_or_add_products(body: NewQuoteRequest) -> QuoteResponse|QuoteDetailResponse:
    """
        Quotes and quote details are stored separately but go together.

        This endpoint will handle both a new unique quote and new products
        for an existing quote.

        For new products on an existing quote, this means that the 'relationship' field
        specifying the quote by its id will required.
    
    """
    data = body.data
    match data:
        case NewQuoteResourceObject():
            print("new top level quote")
        case NewQuoteDetailResourceObject():
            print("new quote details for an existing quote")
    raise HTTPException(status_code=501)

@quotes.patch('/{quote_id}')
async def modify_quote(quote_id: int, body: ExistingQuoteRequest) -> QuoteResponse|QuoteDetailResponse:
    """
        Like new quotes, this endpoint handles patch requests to both the top level quote
        as well as quote details     
    """
    data = body.data
    match data:
        case ExistingQuote():
            print("change top-level quote")
        case ExistingQuoteDetail():
            print("modify details for an existing quote")
    raise HTTPException(status_code=501)