from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.jsonapi.core_models import convert_query
from app.jsonapi.sqla_models import ADPMaterialGroupDiscount, ADPMaterialGroup
from app.adp.models import (
    MatGrpDiscQueryJSONAPI,
    ADPMatGrpDiscResp,
    MatGrpDiscQuery,
    ADPRelatedMatGrpResp,
    ADPMatGrpRelationshipResp,
    NewMatGrpDiscReq,
    ModStageMatGrpDiscDiscReq,
)
from app.jsonapi.core_models import Query

PARENT_PREFIX = "/vendors/adp"
API_TYPE = ADPMaterialGroupDiscount.__jsonapi_type_override__
MATERIAL_GROUPS = ADPMaterialGroup.__jsonapi_type_override__

adp_mat_grp_discs = APIRouter(prefix=f"/{API_TYPE}", tags=["adp", "pricing"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(MatGrpDiscQueryJSONAPI)


@adp_mat_grp_discs.get(
    "",
    response_model=ADPMatGrpDiscResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def mat_grp_disc_collection(
    token: Token, session: NewSession, query: MatGrpDiscQuery = Depends()
) -> ADPMatGrpDiscResp:
    return (
        auth.ADPOperations(token, API_TYPE, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@adp_mat_grp_discs.get(
    "/{mat_grp_id}",
    response_model=ADPMatGrpDiscResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def mat_grp_disc_resource(
    token: Token,
    session: NewSession,
    mat_grp_id: int,
    query: MatGrpDiscQuery = Depends(),
) -> ADPMatGrpDiscResp:
    return (
        auth.ADPOperations(token, API_TYPE, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), obj_id=mat_grp_id)
    )


@adp_mat_grp_discs.get(
    "/{mat_grp_id}/adp-material-groups",
    response_model=ADPRelatedMatGrpResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def mat_grp_disc_related_mat_grp(
    token: Token,
    session: NewSession,
    mat_grp_id: int,
    query: Query = Depends(),
) -> ADPRelatedMatGrpResp:
    return (
        auth.ADPOperations(token, API_TYPE, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            obj_id=mat_grp_id,
            related_resource="adp-material-groups",
        )
    )


@adp_mat_grp_discs.get(
    "/{mat_grp_id}/relationships/adp-material-groups",
    response_model=ADPMatGrpRelationshipResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def mat_grp_disc_mat_grp_relationship(
    token: Token,
    session: NewSession,
    mat_grp_id: int,
    query: Query = Depends(),
) -> ADPMatGrpRelationshipResp:
    return (
        auth.ADPOperations(token, API_TYPE, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            obj_id=mat_grp_id,
            related_resource="adp-material-groups",
            relationship=True,
        )
    )


@adp_mat_grp_discs.post(
    "",
    response_model=ADPMatGrpDiscResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def new_mat_grp_disc(
    token: Token,
    session: NewSession,
    new_discount: NewMatGrpDiscReq,
) -> ADPMatGrpDiscResp:
    if 0 < new_discount.data.attributes.discount < 100:
        return (
            auth.ADPOperations(token, API_TYPE, prefix=PARENT_PREFIX)
            .allow_admin()
            .allow_sca()
            .allow_dev()
            .post(
                session,
                data=new_discount.model_dump(exclude_none=True, by_alias=True),
                primary_id=new_discount.data.relationships.adp_customers.data.id,
            )
        )
    raise HTTPException(
        status.HTTP_400_BAD_REQUEST,
        "discount values must be greater than 0 and less than 100",
    )


@adp_mat_grp_discs.patch(
    "/{mat_grp_id}",
    response_model=ADPMatGrpDiscResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def mat_grp_disc_modification(
    token: Token,
    session: NewSession,
    mat_grp_id: int,
    new_stage: ModStageMatGrpDiscDiscReq,
) -> ADPMatGrpDiscResp:
    return (
        auth.ADPOperations(token, API_TYPE, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session,
            data=new_stage.model_dump(exclude_none=True, by_alias=True),
            obj_id=mat_grp_id,
            primary_id=new_stage.data.relationships.adp_customers.data.id,
        )
    )


@adp_mat_grp_discs.delete(
    "/{mat_grp_id}",
    tags=["jsonapi"],
)
def del_mat_grp_disc(
    token: Token, session: NewSession, mat_grp_id: int, adp_customer_id: int
) -> None:
    return (
        auth.ADPOperations(token, API_TYPE, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session,
            obj_id=mat_grp_id,
            primary_id=adp_customer_id,
        )
    )
