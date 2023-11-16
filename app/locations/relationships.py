from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth

from app.customers.models import RelatedCustomerResponse, CustomerRelationshipsResponse
from app.places.models import RelatedPlaceResponse, PlaceRelationshipsResponse


location_rel = APIRouter(tags=['locations'])

@location_rel.get('/{location_id}/customers')
async def related_customer(
        location_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> RelatedCustomerResponse:
    raise HTTPException(status_code=501)

@location_rel.get('/{location_id}/relationships/customers')
async def location_customer_relationships(
        location_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> CustomerRelationshipsResponse:
    raise HTTPException(status_code=501)

@location_rel.get('/{location_id}/customer-users')
async def related_customer_user(
        location_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> RelatedCustomerResponse:
    raise HTTPException(status_code=501)

@location_rel.get('/{location_id}/relationships/customer-users')
async def location_customer_user_relationships(
        location_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> CustomerRelationshipsResponse:
    raise HTTPException(status_code=501)

@location_rel.get('/{location_id}/places')
async def related_place(
        location_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> RelatedPlaceResponse:
    raise HTTPException(status_code=501)

@location_rel.get('/{location_id}/relationships/places')
async def location_place_relationships(
        location_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> PlaceRelationshipsResponse:
    raise HTTPException(status_code=501)
