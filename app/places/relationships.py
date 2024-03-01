from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth

from app.customers.locations.models import RelatedLocationResponse, LocationRelationshipsResponse
from app.adp.quotes.job_quotes.models import RelatedQuoteResponse, QuoteRelationshipsResponse

place_rel = APIRouter(tags=['places'])

@place_rel.get('/{place_id}/customer-locations')
async def related_location(
        place_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> RelatedLocationResponse:
    raise HTTPException(status_code=501)

@place_rel.get('/{place_id}/relationships/customer-locations')
async def place_location_relationships(
        place_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> LocationRelationshipsResponse:
    raise HTTPException(status_code=501)

@place_rel.get('/{place_id}/adp-quotes')
async def related_quotes(
        place_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> RelatedQuoteResponse:
    raise HTTPException(status_code=501)

@place_rel.get('/{place_id}/relationships/adp-quotes')
async def place_quotes_relationships(
        place_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> QuoteRelationshipsResponse:
    raise HTTPException(status_code=501)