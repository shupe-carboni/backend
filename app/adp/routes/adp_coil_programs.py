from typing import Annotated
from functools import partial
from fastapi import HTTPException, Depends, status
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.adp.extraction.models import build_model_attributes
from app.adp.models import (
    CoilProgQuery,
    CoilProgQueryJSONAPI,
    CoilProgResp,
    NewCoilRObjFull,
    NewCoilRObj,
    ModStageCoilReq,
)
from app.jsonapi.sqla_models import serializer, ADPCoilProgram, ADPCustomer
from app.jsonapi.core_models import convert_query

ADP_COILS_RESOURCE = ADPCoilProgram.__jsonapi_type_override__
ADP_CUSTOMERS_RESOURCE = ADPCustomer.__jsonapi_type_override__
coil_progs = APIRouter(prefix=f"/{ADP_COILS_RESOURCE}", tags=["coils", "programs"])

ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(CoilProgQueryJSONAPI)


@coil_progs.get(
    "", response_model=CoilProgResp, response_model_exclude_none=True, tags=["jsonapi"]
)
def all_coil_programs(
    token: ADPPerm, session: NewSession, query: CoilProgQuery = Depends()
) -> CoilProgResp:
    """List out all coil programs.
    An SCA admin or employee will see all programs that exist.
    A customer will see only their own programs"""
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session=session, resource=ADP_COILS_RESOURCE, query=converter(query))
    )


@coil_progs.get(
    "/{program_product_id}",
    response_model=CoilProgResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def coil_program_product(
    token: ADPPerm,
    session: NewSession,
    program_product_id: int,
    query: CoilProgQuery = Depends(),
) -> CoilProgResp:
    """get a specific product from the coil programs"""
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=ADP_COILS_RESOURCE,
            query=converter(query),
            obj_id=program_product_id,
        )
    )


def build_full_model_obj(session: Session, new_coil: NewCoilRObj):
    model_num = new_coil.attributes.model_number
    adp_customer_id = new_coil.relationships.adp_customers.data.id
    model_w_attrs = build_model_attributes(
        session=session, model=model_num, adp_customer_id=adp_customer_id
    )
    json_api_data = dict(
        data=NewCoilRObjFull(
            attributes=model_w_attrs.to_dict(),
            relationships=new_coil.relationships,
        ).model_dump(by_alias=True)
    )
    return json_api_data


@coil_progs.post(
    "",
    response_model=CoilProgResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def add_to_coil_program(
    token: ADPPerm, session: NewSession, new_coil: NewCoilRObj
) -> CoilProgResp:
    json_api_data = partial(build_full_model_obj, session, new_coil)
    adp_customer_id = new_coil.relationships.adp_customers.data.id
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .post(
            session=session,
            resource=ADP_COILS_RESOURCE,
            data=json_api_data,
            customer_id=adp_customer_id,
        )
    )


@coil_progs.patch(
    "/{program_product_id}",
    response_model=CoilProgResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def change_product_status(
    token: ADPPerm,
    session: NewSession,
    program_product_id: int,
    new_stage: ModStageCoilReq,
) -> CoilProgResp:
    """change the stage of a program coil
    Stage: ACITVE, PROPOSED, REJECTED, REMOVED
    examples:
        PROPOSED -> ACTIVE
        ACTIVE -> REMOVED
    """
    adp_customer_id = new_stage.data.relationships.adp_customers.data.id
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            resource=ADP_COILS_RESOURCE,
            data=new_stage.model_dump(by_alias=True),
            customer_id=adp_customer_id,
            obj_id=program_product_id,
        )
    )


@coil_progs.delete("/{program_product_id}")
def permanently_delete_record(
    token: ADPPerm,
    session: NewSession,
    program_product_id: int,
) -> None:
    if token.permissions >= auth.Permissions.sca_admin:
        return serializer.delete_resource(
            session, data={}, api_type=ADP_COILS_RESOURCE, obj_id=program_product_id
        )
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)


@coil_progs.get("/{program_product_id}/adp-customers")
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
            resource=ADP_COILS_RESOURCE,
            query={},
            obj_id=program_product_id,
            relationship=False,
            related_resource=ADP_CUSTOMERS_RESOURCE,
        )
    )


@coil_progs.get("/{program_product_id}/relationships/adp-customers")
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
            resource=ADP_COILS_RESOURCE,
            query={},
            obj_id=program_product_id,
            relationship=True,
            related_resource=ADP_CUSTOMERS_RESOURCE,
        )
    )
