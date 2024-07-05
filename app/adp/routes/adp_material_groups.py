from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
from app.adp.models import (
    ADPMaterialGroupResp,
    ADPMaterialGroupQuery,
    ADPMaterialGroupQueryJSONAPI,
    RelatedADPMatGrpDiscResp,
    ADPMatGrpDiscRelationshipsResp,
)
from app.jsonapi.sqla_models import ADPMaterialGroup

PARENT_PREFIX = "/vendors/adp"
ADP_MATERIAL_GROUPS = ADPMaterialGroup.__jsonapi_type_override__

adp_material_groups = APIRouter(prefix=f"/{ADP_MATERIAL_GROUPS}", tags=["adp", ""])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(ADPMaterialGroupQueryJSONAPI)


@adp_material_groups.get(
    "",
    response_model=ADPMaterialGroupResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def adp_material_group_collection(
    token: Token, session: NewSession, query: ADPMaterialGroupQuery = Depends()
) -> ADPMaterialGroupResp:
    return (
        auth.ADPOperations(token, ADPMaterialGroup, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@adp_material_groups.get(
    "/{adp_material_group_id}",
    response_model=ADPMaterialGroupResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def adp_material_group_resource(
    token: Token,
    session: NewSession,
    adp_material_group_id: int,
    query: ADPMaterialGroupQuery = Depends(),
) -> ADPMaterialGroupResp:
    return (
        auth.ADPOperations(token, ADPMaterialGroup, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), adp_material_group_id)
    )


@adp_material_groups.get(
    "/{adp_material_group_id}/adp-material-group-discounts",
    response_model=RelatedADPMatGrpDiscResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def adp_material_group_related_adp_material_group_discounts(
    token: Token,
    session: NewSession,
    adp_material_group_id: int,
    query: ADPMaterialGroupQuery = Depends(),
) -> RelatedADPMatGrpDiscResp:
    return (
        auth.ADPOperations(token, ADPMaterialGroup, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .get(
            session,
            converter(query),
            adp_material_group_id,
            "adp-material-group-discounts",
        )
    )


@adp_material_groups.get(
    "/{adp_material_group_id}/relationships/adp-material-group-discounts",
    response_model=ADPMatGrpDiscRelationshipsResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def adp_material_group_relationships_adp_material_group_discounts(
    token: Token,
    session: NewSession,
    adp_material_group_id: int,
    query: ADPMaterialGroupQuery = Depends(),
) -> ADPMatGrpDiscRelationshipsResp:
    return (
        auth.ADPOperations(token, ADPMaterialGroup, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .get(
            session,
            converter(query),
            adp_material_group_id,
            "adp-material-group-discounts",
            True,
        )
    )


@adp_material_groups.delete(
    "/{adp_material_group_id}",
    tags=["jsonapi"],
)
async def del_adp_material_group(
    token: Token,
    session: NewSession,
    adp_material_group_id: int,
) -> None:
    return (
        auth.ADPOperations(token, ADPMaterialGroup, PARENT_PREFIX)
        .allow_admin()
        .delete(session, obj_id=adp_material_group_id)
    )
