from typing import Annotated
from functools import partial
from fastapi import Depends
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.adp.extraction.models import build_model_attributes
from app.adp.models import (
    CoilProgQuery,
    CoilProgQueryJSONAPI,
    CoilProgResp,
    NewCoilRObjFull,
    NewCoilRequest,
    ModStageCoilReq,
)
from app.jsonapi.sqla_models import ADPCoilProgram, ADPCustomer
from app.jsonapi.core_models import convert_query
from app.jsonapi.sqla_jsonapi_ext import MAX_PAGE_SIZE

ADP_COILS_RESOURCE = ADPCoilProgram.__jsonapi_type_override__
ADP_CUSTOMERS_RESOURCE = ADPCustomer.__jsonapi_type_override__
coil_progs = APIRouter(prefix=f"/{ADP_COILS_RESOURCE}", tags=["coils", "programs"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(CoilProgQueryJSONAPI)

RESOURCE_EXCLUSIONS = {
    "data": {
        "attributes": {
            "ratings_ac_txv",
            "ratings_hp_txv",
            "ratings_piston",
            "ratings_field_txv",
        }
    }
}

COLLECTION_EXCLUSIONS = {
    "data": {
        i: {
            "attributes": {
                "ratings_ac_txv",
                "ratings_hp_txv",
                "ratings_piston",
                "ratings_field_txv",
            }
        }
        for i in range(MAX_PAGE_SIZE)
    }
}


@coil_progs.get(
    "",
    response_model=CoilProgResp,
    response_model_exclude_none=True,
    response_model_exclude=COLLECTION_EXCLUSIONS,
    tags=["jsonapi"],
)
def all_coil_programs(
    token: Token, session: NewSession, query: CoilProgQuery = Depends()
) -> CoilProgResp:
    """List out all coil programs.
    An SCA admin or employee will see all programs that exist.
    A customer will see only their own programs"""
    return (
        auth.ADPOperations(token, ADP_COILS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session=session, query=converter(query))
    )


@coil_progs.get(
    "/{program_product_id}",
    response_model=CoilProgResp,
    response_model_exclude_none=True,
    response_model_exclude=RESOURCE_EXCLUSIONS,
    tags=["jsonapi"],
)
def coil_program_product(
    token: Token,
    session: NewSession,
    program_product_id: int,
    query: CoilProgQuery = Depends(),
) -> CoilProgResp:
    """get a specific product from the coil programs"""
    return (
        auth.ADPOperations(token, ADP_COILS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            query=converter(query),
            obj_id=program_product_id,
        )
    )


def build_full_model_obj(session: Session, new_coil: NewCoilRequest):
    model_num = new_coil.data.attributes.model_number
    adp_customer_id = new_coil.data.relationships.adp_customers.data.id
    model_w_attrs = build_model_attributes(
        session=session, model=model_num, adp_customer_id=adp_customer_id
    )
    json_api_data = dict(
        data=NewCoilRObjFull(
            attributes=model_w_attrs.to_dict(),
            relationships=new_coil.data.relationships,
        ).model_dump(by_alias=True, exclude_none=True)
    )
    return json_api_data


@coil_progs.post(
    "",
    response_model=CoilProgResp,
    response_model_exclude_none=True,
    response_model_exclude=RESOURCE_EXCLUSIONS,
    tags=["jsonapi"],
)
def add_to_coil_program(
    token: Token, session: NewSession, new_coil: NewCoilRequest
) -> CoilProgResp:
    json_api_data = partial(build_full_model_obj, session, new_coil)
    adp_customer_id = new_coil.data.relationships.adp_customers.data.id
    return (
        auth.ADPOperations(token, ADP_COILS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .post(
            session=session,
            data=json_api_data,
            primary_id=adp_customer_id,
        )
    )


@coil_progs.patch(
    "/{program_product_id}",
    response_model=CoilProgResp,
    response_model_exclude_none=True,
    response_model_exclude=RESOURCE_EXCLUSIONS,
    tags=["jsonapi"],
)
def change_product_status(
    token: Token,
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
        auth.ADPOperations(token, ADP_COILS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=new_stage.model_dump(exclude_none=True, by_alias=True),
            primary_id=adp_customer_id,
            obj_id=program_product_id,
        )
    )


@coil_progs.delete("/{program_product_id}", tags=["jsonapi"])
def permanently_delete_record(
    token: Token, session: NewSession, program_product_id: int, adp_customer_id: int
) -> None:
    return (
        auth.ADPOperations(token, ADP_COILS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, program_product_id, adp_customer_id)
    )


@coil_progs.get("/{program_product_id}/" + ADP_CUSTOMERS_RESOURCE)
def get_related_customer(
    token: Token,
    session: NewSession,
    program_product_id: int,
):
    return (
        auth.ADPOperations(token, ADP_COILS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            obj_id=program_product_id,
            relationship=False,
            related_resource=ADP_CUSTOMERS_RESOURCE,
        )
    )


@coil_progs.get("/{program_product_id}/relationships/" + ADP_CUSTOMERS_RESOURCE)
def get_customer_relationship(
    token: Token,
    session: NewSession,
    program_product_id: int,
):
    return (
        auth.ADPOperations(token, ADP_COILS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            obj_id=program_product_id,
            relationship=True,
            related_resource=ADP_CUSTOMERS_RESOURCE,
        )
    )
