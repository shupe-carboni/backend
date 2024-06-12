from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.jsonapi.core_models import convert_query
from app.jsonapi.sqla_models import ADPSNP
from app.adp.models import (
    ADPSNPQueryJSONAPI,
    ADPSNPResp,
    ADPSNPQuery,
    # NewADPSNPReq,
    # ModStageADPSNPDiscReq,
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
