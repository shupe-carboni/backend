from typing import Annotated
from fastapi import HTTPException, Depends, status
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.adp.models import (
    AirHandlerProgResp,
    AirHandlerProgQuery,
    AHProgQueryJSONAPI,
    NewAHRObj,
    ModStageAHReq,
)
from app.jsonapi.sqla_models import serializer, ADPAHProgram
from app.jsonapi.core_models import convert_query

ADP_AIR_HANDLERS_RESOURCE = ADPAHProgram.__jsonapi_type_override__
ah_progs = APIRouter(
    prefix=f"/{ADP_AIR_HANDLERS_RESOURCE}", tags=["air handlers", "programs"]
)

ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(AHProgQueryJSONAPI)


@ah_progs.get(
    "",
    response_model=AirHandlerProgResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def all_ah_programs(
    token: ADPPerm,
    session: NewSession,
    query: AirHandlerProgQuery = Depends(),
) -> AirHandlerProgResp:
    """List out all ah programs.
    An SCA admin or employee will see all programs that exist.
    A customer will see only their own programs"""
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session, resource=ADP_AIR_HANDLERS_RESOURCE, query=converter(query)
        )
    )


@ah_progs.get(
    "/{program_product_id}",
    response_model=AirHandlerProgResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def ah_program_product(
    token: ADPPerm,
    session: NewSession,
    program_product_id: int,
    query: AirHandlerProgQuery = Depends(),
) -> AirHandlerProgResp:
    """get a specific product from the ah programs"""
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=ADP_AIR_HANDLERS_RESOURCE,
            query=converter(query),
            obj_id=program_product_id,
        )
    )


@ah_progs.post(
    "/{adp_customer_id}",
    response_model=AirHandlerProgResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def add_to_ah_program(
    token: ADPPerm,
    session: NewSession,
    adp_customer_id: int,
    new_ah: NewAHRObj,
) -> AirHandlerProgResp:
    """create a new product in an existing program"""
    if token.permissions >= auth.Permissions.sca_employee:
        model_num = new_ah.attributes.model_number
        # new_id = add_model_to_program(session=session, model=model_num, adp_customer_id=adp_customer_id)
        return serializer.get_resource(
            session=session,
            query=converter(AirHandlerProgQuery()),
            api_type=ADP_AIR_HANDLERS_RESOURCE,
            # obj_id=new_id,
            obj_only=True,
            permitted_ids=None,
        )
    else:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@ah_progs.patch(
    "/{program_product_id}",
    response_model=AirHandlerProgResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def change_product_status(
    token: ADPPerm,
    session: NewSession,
    program_product_id: int,
    new_stage: ModStageAHReq,
) -> AirHandlerProgResp:
    adp_customer_id = new_stage.data.relationships.adp_customers.data.id
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            resource=ADP_AIR_HANDLERS_RESOURCE,
            data=new_stage.model_dump(by_alias=True),
            customer_id=adp_customer_id,
            obj_id=program_product_id,
        )
    )


@ah_progs.delete("/{program_product_id}", tags=["jsonapi"])
def delete_ah_program_product(
    token: ADPPerm,
    session: NewSession,
    program_product_id: int,
):
    if token.permissions >= auth.Permissions.sca_admin:
        return serializer.delete_resource(
            session, {}, ADP_AIR_HANDLERS_RESOURCE, program_product_id
        )
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)


@ah_progs.get("/{program_product_id}/adp-customers")
def get_related_customer(
    token: ADPPerm,
    session: NewSession,
    program_product_id: int,
):
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=ADP_AIR_HANDLERS_RESOURCE,
            query={},
            obj_id=program_product_id,
            relationship=False,
            related_resource="adp-customers",
        )
    )


@ah_progs.get("/{program_product_id}/relationships/adp-customers")
def get_customer_relationship(
    token: ADPPerm,
    session: NewSession,
    program_product_id: int,
):
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=ADP_AIR_HANDLERS_RESOURCE,
            query={},
            obj_id=program_product_id,
            relationship=True,
            related_resource="adp-customers",
        )
    )
