
from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app import auth
from app.db import SCA_DB
from app.customers.locations.models import RelatedLocationResponse, LocationRelationshipsResponse
from app.adp.models import (
    RelatedCustomerResponse,
    CustomersRelResp,
    RelatedADPCustomerTermsResp,
    ADPCustomerTermsRelationshipsResp
)
from app.auth import ADPPermPriority
from app.jsonapi.sqla_models import serializer

API_TYPE = 'customers'
customer_rel = APIRouter(tags=[API_TYPE])
CustomersPerm = Annotated[auth.VerifiedToken, Depends(auth.customers_perms_present)]
ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_perms_present)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]

@customer_rel.get('/{customer_id}/customer-locations', response_model=RelatedLocationResponse, response_model_exclude_none=True)
async def related_location(
        session: NewSession,
        customer_id: int,
        token: CustomersPerm,
    ) -> RelatedLocationResponse:
    return serializer.get_related(session=session, query={}, api_type=API_TYPE, obj_id=customer_id, rel_key='customer-locations')

@customer_rel.get('/{customer_id}/relationships/customer-locations', response_model=LocationRelationshipsResponse, response_model_exclude_none=True)
async def customer_location_relationships(
        session: NewSession,
        customer_id: int,
        token: CustomersPerm,
    ) -> LocationRelationshipsResponse:
    return serializer.get_relationship(session=session, query={}, api_type=API_TYPE, obj_id=customer_id, rel_key='customer-locations')

@customer_rel.get('/{customer_id}/adp-customers', response_model=RelatedCustomerResponse, response_model_exclude_none=True)
async def related_adp_customers(
        session: NewSession,
        customer_id: int,
        token: ADPPerm,
    ) -> RelatedCustomerResponse:
    if token.permissions.get('adp') >= ADPPermPriority.customer_admin:
        return serializer.get_related(session=session, query={}, api_type=API_TYPE, obj_id=customer_id, rel_key='adp-customers')
    else:
        raise HTTPException(status_code=401)

@customer_rel.get('/{customer_id}/relationships/adp-customers', response_model=CustomersRelResp, response_model_exclude_none=True)
async def adp_customer_relationships(
        session: NewSession,
        customer_id: int,
        token: ADPPerm,
    ) -> CustomersRelResp:
    if token.permissions.get('adp') >= ADPPermPriority.customer_admin:
        return serializer.get_relationship(session=session, query={}, api_type=API_TYPE, obj_id=customer_id, rel_key='adp-customers')
    else:
        raise HTTPException(status_code=401)

@customer_rel.get('/{customer_id}/adp-customer-terms', response_model=RelatedADPCustomerTermsResp, response_model_exclude_none=True)
async def related_adp_customer_terms(
        session: NewSession,
        customer_id: int,
        token: ADPPerm,
    ) -> RelatedADPCustomerTermsResp:
    if token.permissions.get('adp') >= ADPPermPriority.customer_admin:
        return serializer.get_related(session=session, query={}, api_type=API_TYPE, obj_id=customer_id, rel_key='adp-customer-terms')
    else:
        raise HTTPException(status_code=401)

@customer_rel.get('/{customer_id}/relationships/adp-customer-terms', response_model=ADPCustomerTermsRelationshipsResp, response_model_exclude_none=True)
async def adp_customer_terms_relationships(
        session: NewSession,
        customer_id: int,
        token: ADPPerm,
    ) -> ADPCustomerTermsRelationshipsResp:
    if token.permissions.get('adp') >= ADPPermPriority.customer_admin:
        return serializer.get_relationship(session=session, query={}, api_type=API_TYPE, obj_id=customer_id, rel_key='adp-customer-terms')
    else:
        raise HTTPException(status_code=401)