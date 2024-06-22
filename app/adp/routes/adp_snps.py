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
    NewADPSNPReq,
    ModStageSNPReq,
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
        auth.ADPOperations(token, ADPSNP, prefix=PARENT_PREFIX)
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
        auth.ADPOperations(token, ADPSNP, prefix=PARENT_PREFIX)
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
        auth.ADPOperations(token, ADPSNP, prefix=PARENT_PREFIX)
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
        auth.ADPOperations(token, ADPSNP, prefix=PARENT_PREFIX)
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


@adp_snps.post(
    "",
    response_model=ADPSNPResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def new_snp(
    token: Token,
    session: NewSession,
    new_snp: NewADPSNPReq,
) -> ADPSNPResp:
    if 0 >= new_snp.data.attributes.price:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "a special net price must be greater than 0",
        )
    return (
        auth.ADPOperations(token, ADPSNP, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session,
            data=new_snp.model_dump(exclude_none=True, by_alias=True),
            primary_id=new_snp.data.relationships.adp_customers.data.id,
        )
    )


@adp_snps.patch(
    "/{snp_id}",
    response_model=ADPSNPResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def snp_modification(
    token: Token,
    session: NewSession,
    snp_id: int,
    new_stage: ModStageSNPReq,
) -> ADPSNPResp:
    return (
        auth.ADPOperations(token, ADPSNP, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session,
            data=new_stage.model_dump(exclude_none=True, by_alias=True),
            obj_id=snp_id,
            primary_id=new_stage.data.relationships.adp_customers.data.id,
        )
    )


@adp_snps.delete(
    "/{snp_id}",
    tags=["jsonapi"],
)
def del_snp(
    token: Token, session: NewSession, snp_id: int, adp_customer_id: int
) -> None:
    return (
        auth.ADPOperations(token, ADPSNP, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session,
            obj_id=snp_id,
            primary_id=adp_customer_id,
        )
    )
