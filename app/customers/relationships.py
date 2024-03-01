
from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth

from app.customers.locations.models import RelatedLocationResponse, LocationRelationshipsResponse
from app.adp.models import CustomersResp

customer_rel = APIRouter(tags=['customers'])
CustomersPerm = Annotated[auth.VerifiedToken, Depends(auth.customers_perms_present)]
ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_perms_present)]

@customer_rel.get('/{customer_id}/locations')
async def related_location(
        customer_id: int,
        token: CustomersPerm,
    ) -> RelatedLocationResponse:
    raise HTTPException(status_code=501)

@customer_rel.get('/{customer_id}/relationships/locations')
async def customer_location_relationships(
        customer_id: int,
        token: CustomersPerm,
    ) -> LocationRelationshipsResponse:
    raise HTTPException(status_code=501)

@customer_rel.get('/{customer_id}/adp-customers')
async def related_location(
        customer_id: int,
        token: ADPPerm,
    ) -> CustomersResp:
    raise HTTPException(status_code=501)

@customer_rel.get('/{customer_id}/relationships/adp-customers')
async def customer_location_relationships(
        customer_id: int,
        token: ADPPerm,
    ) -> LocationRelationshipsResponse:
    raise HTTPException(status_code=501)

@customer_rel.get('/{customer_id}/adp-customer-terms')
async def related_location(
        customer_id: int,
        token: ADPPerm,
    ) -> RelatedLocationResponse:
    raise HTTPException(status_code=501)

@customer_rel.get('/{customer_id}/relationships/adp-customer-terms')
async def customer_location_relationships(
        customer_id: int,
        token: ADPPerm,
    ) -> LocationRelationshipsResponse:
    raise HTTPException(status_code=501)