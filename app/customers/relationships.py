from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app import auth
from app.db import SCA_DB
from app.customers.locations.models import RelatedLocationResponse, LocationRelationshipsResponse
from app.adp.models import (
    RelatedCustomerResponse, CustomersRelResp,
    RelatedADPCustomerTermsResp, ADPCustomerTermsRelationshipsResp
)
from app.auth import ADPPermPriority
from app.jsonapi.sqla_models import SCACustomer

API_TYPE = SCACustomer.__jsonapi_type_override__
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
    return auth.secured_get_query(
        db=SCA_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['adp'],
        resource=API_TYPE,
        query={},
        obj_id=customer_id,
        relationship=False,
        related_resource='customer-locations'
    )

@customer_rel.get('/{customer_id}/relationships/customer-locations', response_model=LocationRelationshipsResponse, response_model_exclude_none=True)
async def customer_location_relationships(
        session: NewSession,
        customer_id: int,
        token: CustomersPerm,
    ) -> LocationRelationshipsResponse:
    return auth.secured_get_query(
        db=SCA_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['adp'],
        resource=API_TYPE,
        query={},
        obj_id=customer_id,
        relationship=True,
        related_resource='customer-locations'
    )

@customer_rel.get('/{customer_id}/adp-customers', response_model=RelatedCustomerResponse, response_model_exclude_none=True)
async def related_adp_customers(
        session: NewSession,
        customer_id: int,
        token: ADPPerm,
    ) -> RelatedCustomerResponse:
    if token.permissions.get('adp') >= ADPPermPriority.customer_admin:
        return auth.secured_get_query(
            db=SCA_DB,
            session=session,
            token=token,
            auth_scheme=auth.Permissions['adp'],
            resource=API_TYPE,
            query={},
            obj_id=customer_id,
            relationship=False,
            related_resource='adp-customers'
        )
    else:
        raise HTTPException(status_code=401)

@customer_rel.get('/{customer_id}/relationships/adp-customers', response_model=CustomersRelResp, response_model_exclude_none=True)
async def adp_customer_relationships(
        session: NewSession,
        customer_id: int,
        token: ADPPerm,
    ) -> CustomersRelResp:
    if token.permissions.get('adp') >= ADPPermPriority.customer_admin:
        return auth.secured_get_query(
            db=SCA_DB,
            session=session,
            token=token,
            auth_scheme=auth.Permissions['adp'],
            resource=API_TYPE,
            query={},
            obj_id=customer_id,
            relationship=True,
            related_resource='adp-customers'
        )
    else:
        raise HTTPException(status_code=401)

@customer_rel.get('/{customer_id}/adp-customer-terms', response_model=RelatedADPCustomerTermsResp, response_model_exclude_none=True)
async def related_adp_customer_terms(
        session: NewSession,
        customer_id: int,
        token: ADPPerm,
    ) -> RelatedADPCustomerTermsResp:
    if token.permissions.get('adp') >= ADPPermPriority.customer_admin:
        return auth.secured_get_query(
            db=SCA_DB,
            session=session,
            token=token,
            auth_scheme=auth.Permissions['adp'],
            resource=API_TYPE,
            query={},
            obj_id=customer_id,
            relationship=False,
            related_resource='adp-customer-terms'
        )
    else:
        raise HTTPException(status_code=401)

@customer_rel.get('/{customer_id}/relationships/adp-customer-terms', response_model=ADPCustomerTermsRelationshipsResp, response_model_exclude_none=True)
async def adp_customer_terms_relationships(
        session: NewSession,
        customer_id: int,
        token: ADPPerm,
    ) -> ADPCustomerTermsRelationshipsResp:
    if token.permissions.get('adp') >= ADPPermPriority.customer_admin:
        return auth.secured_get_query(
            db=SCA_DB,
            session=session,
            token=token,
            auth_scheme=auth.Permissions['adp'],
            resource=API_TYPE,
            query={},
            obj_id=customer_id,
            relationship=True,
            related_resource='adp-customer-terms'
        )
    else:
        raise HTTPException(status_code=401)