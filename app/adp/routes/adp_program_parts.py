from typing import Annotated
from fastapi import HTTPException, Depends, status
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.adp.models import PartsQuery, PartsResp, PartsQueryJSONAPI, NewPartRequest
from app.jsonapi.sqla_models import ADPProgramPart
from app.jsonapi.core_models import convert_query

ADP_PARTS_RESOURCE = ADPProgramPart.__jsonapi_type_override__
prog_parts = APIRouter(prefix=f"/{ADP_PARTS_RESOURCE}", tags=["parts", "programs"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(PartsQueryJSONAPI)


@prog_parts.get(
    "", response_model=PartsResp, response_model_exclude_none=True, tags=["jsonapi"]
)
def all_parts(
    token: Token, session: NewSession, query: PartsQuery = Depends()
) -> PartsResp:
    return (
        auth.ADPOperations(token, ADP_PARTS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session=session, query=converter(query))
    )


@prog_parts.get(
    "/{part_id}",
    response_model=PartsResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def a_part(
    token: Token, part_id: int, session: NewSession, query: PartsQuery = Depends()
) -> PartsResp:
    return (
        auth.ADPOperations(token, ADP_PARTS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            query=converter(query),
            obj_id=part_id,
        )
    )


@prog_parts.post(
    "", response_model=PartsResp, response_model_exclude_none=True, tags=["jsonapi"]
)
async def add_program_parts(
    token: Token,
    session: NewSession,
    part: NewPartRequest,
) -> PartsResp:
    customer_id = part.data.relationships.adp_customers.data.id
    return (
        auth.ADPOperations(token, ADP_PARTS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .post(
            session=session,
            data=part.model_dump(by_alias=True),
            primary_id=customer_id,
        )
    )


@prog_parts.patch("/{part_id}", tags=["jsonapi", "not implemented"])
def modify_part(token: Token):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Parts/Accessories may be added or removed, but not modified",
    )


@prog_parts.delete("/{part_id}", tags=["jsonapi", "admin"])
def delete_part(token: Token, session: NewSession, part_id: int, adp_customer_id: int):
    return (
        auth.ADPOperations(token, ADP_PARTS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session=session, obj_id=part_id, primary_id=adp_customer_id)
    )
