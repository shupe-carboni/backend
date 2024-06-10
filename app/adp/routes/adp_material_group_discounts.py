from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.jsonapi.core_models import convert_query
from app.jsonapi.sqla_models import ADPMaterialGroupDiscount, ADPMaterialGroup
from app.adp.models import MatGrpsQueryJSONAPI, ADPMatGrpsResp, MatGrpsQuery

API_TYPE = ADPMaterialGroupDiscount.__jsonapi_type_override__
MATERIAL_GROUPS = ADPMaterialGroup.__jsonapi_type_override__

adp_mat_grp_discs = APIRouter(prefix=f"/{API_TYPE}", tags=["adp", "pricing"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(MatGrpsQueryJSONAPI)


@adp_mat_grp_discs.get(
    "",
    response_model=ADPMatGrpsResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def mat_grp_disc_collection(
    token: Token, session: NewSession, query: MatGrpsQuery = Depends()
) -> ADPMatGrpsResp:
    return (
        auth.ADPOperations(token, API_TYPE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )
