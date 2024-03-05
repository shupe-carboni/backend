
from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app import auth
from app.db import SCA_DB
from app.customers.locations.models import RelatedLocationResponse, LocationRelationshipsResponse
from app.adp.models import CustomersResp
from app.jsonapi.sqla_models import serializer

api_type = 'customers'
customer_rel = APIRouter(tags=['customers'])
CustomersPerm = Annotated[auth.VerifiedToken, Depends(auth.customers_perms_present)]
ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_perms_present)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]

@customer_rel.get('/{customer_id}/customer-locations', response_model=RelatedLocationResponse, response_model_exclude_none=True)
async def related_location(
        session: NewSession,
        customer_id: int,
        token: CustomersPerm,
    ) -> RelatedLocationResponse:
    return serializer.get_related(session=session, query={}, api_type=api_type, obj_id=customer_id, rel_key='customer-locations')

@customer_rel.get('/{customer_id}/relationships/customer-locations')
async def customer_location_relationships(
        session: NewSession,
        customer_id: int,
        token: CustomersPerm,
    ) -> LocationRelationshipsResponse:
    raise HTTPException(status_code=501)

@customer_rel.get('/{customer_id}/adp-customers')
async def related_location(
        session: NewSession,
        customer_id: int,
        token: ADPPerm,
    ) -> CustomersResp:
    raise HTTPException(status_code=501)

@customer_rel.get('/{customer_id}/relationships/adp-customers')
async def customer_location_relationships(
        session: NewSession,
        customer_id: int,
        token: ADPPerm,
    ) -> LocationRelationshipsResponse:
    raise HTTPException(status_code=501)

@customer_rel.get('/{customer_id}/adp-customer-terms')
async def related_location(
        session: NewSession,
        customer_id: int,
        token: ADPPerm,
    ) -> RelatedLocationResponse:
    raise HTTPException(status_code=501)

@customer_rel.get('/{customer_id}/relationships/adp-customer-terms')
async def customer_location_relationships(
        session: NewSession,
        customer_id: int,
        token: ADPPerm,
    ) -> LocationRelationshipsResponse:
    raise HTTPException(status_code=501)