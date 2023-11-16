
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth

from app.locations.models import RelatedLocationResponse, LocationRelationshipsResponse

customer_rel = APIRouter(tags=['customers'])

@customer_rel.get('/{customer_id}/locations')
async def related_location(
        customer_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> RelatedLocationResponse:
    raise HTTPException(status_code=501)

@customer_rel.get('/{customer_id}/relationships/locations')
async def customer_location_relationships(
        customer_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> LocationRelationshipsResponse:
    raise HTTPException(status_code=501)