from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth
from app.adp.quotes.job_quotes.models import RelatedQuoteResponse, QuoteRelationshipsResponse

product_rel = APIRouter(prefix='/products', tags=['products'])

@product_rel.get('/{product_id}/quotes')
async def related_quotes(
        product_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> RelatedQuoteResponse:
    raise HTTPException(status_code=501)

@product_rel.get('/{product_id}/relationships/quotes')
async def product_quotes_relationships(
        product_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> QuoteRelationshipsResponse:
    raise HTTPException(status_code=501)
