from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.jsonapi.core_models import convert_query
from app.jsonapi.sqla_models import ADPSNP, ADPCustomer
from app.adp.models import (
    ADPSNPQueryJSONAPI,
    ADPSNPResp,
    ADPSNPQuery,
    # NewADPSNPReq,
    # ModStageADPSNPDiscReq,
    RelatedCustomerResponse,
    CustomersRelResp,
)

PARENT_PREFIX = "/vendors/adp"
API_TYPE = ADPSNP.__jsonapi_type_override__

adp_snps = APIRouter(prefix=f"/{API_TYPE}", tags=["adp", "pricing"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(ADPSNPQueryJSONAPI)


@adp_snps.get(
    "",
    response_model=ADPSNPResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def snps_collection(
    token: Token, session: NewSession, query: ADPSNPQuery = Depends()
) -> ADPSNPResp:
    return (
        auth.ADPOperations(token, API_TYPE, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, query=converter(query))
    )


@adp_snps.get(
    "/{snp_id}",
    response_model=ADPSNPResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def an_snp(
    token: Token, session: NewSession, snp_id: int, query: ADPSNPQuery = Depends()
) -> ADPSNPResp:
    return (
        auth.ADPOperations(token, API_TYPE, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, query=converter(query), obj_id=snp_id)
    )


@adp_snps.get(
    "/{snp_id}/" + ADPCustomer.__jsonapi_type_override__,
    response_model=RelatedCustomerResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def snp_related_adp_customers(
    token: Token, session: NewSession, snp_id: int
) -> RelatedCustomerResponse:
    return (
        auth.ADPOperations(token, API_TYPE, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            obj_id=snp_id,
            related_resource=ADPCustomer.__jsonapi_type_override__,
        )
    )


@adp_snps.get(
    "/{snp_id}/relationships/" + ADPCustomer.__jsonapi_type_override__,
    response_model=CustomersRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def snp_adp_customer_relationships(
    token: Token, session: NewSession, snp_id: int
) -> CustomersRelResp:
    return (
        auth.ADPOperations(token, API_TYPE, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            obj_id=snp_id,
            related_resource=ADPCustomer.__jsonapi_type_override__,
            relationship=True,
        )
    )
