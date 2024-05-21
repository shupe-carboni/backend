from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from functools import partial

from app import auth
from app.db import Session, ADP_DB
from app.adp.models import (
    AirHandlerProgResp,
    AirHandlerProgQuery,
    AHProgQueryJSONAPI,
    NewAHRequest,
    ModStageAHReq,
    NewAHRObjFull,
)
from app.adp.extraction.models import build_model_attributes
from app.jsonapi.sqla_models import ADPAHProgram, ADPCustomer
from app.jsonapi.core_models import convert_query
from app.jsonapi.sqla_jsonapi_ext import MAX_PAGE_SIZE

ADP_AIR_HANDLERS_RESOURCE = ADPAHProgram.__jsonapi_type_override__
ADP_CUSTOMERS_RESOURCE = ADPCustomer.__jsonapi_type_override__
ah_progs = APIRouter(
    prefix=f"/{ADP_AIR_HANDLERS_RESOURCE}", tags=["air handlers", "programs"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(AHProgQueryJSONAPI)

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


@ah_progs.get(
    "",
    response_model=AirHandlerProgResp,
    response_model_exclude_none=True,
    response_model_exclude=COLLECTION_EXCLUSIONS,
    tags=["jsonapi"],
)
def all_ah_programs(
    token: Token,
    session: NewSession,
    query: AirHandlerProgQuery = Depends(),
) -> AirHandlerProgResp:
    """List out all ah programs.
    An SCA admin or employee will see all programs that exist.
    A customer will see only their own programs"""
    return (
        auth.ADPOperations(token, ADP_AIR_HANDLERS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session=session, query=converter(query))
    )


@ah_progs.get(
    "/{program_product_id}",
    response_model=AirHandlerProgResp,
    response_model_exclude_none=True,
    response_model_exclude=RESOURCE_EXCLUSIONS,
    tags=["jsonapi"],
)
def ah_program_product(
    token: Token,
    session: NewSession,
    program_product_id: int,
    query: AirHandlerProgQuery = Depends(),
) -> AirHandlerProgResp:
    """get a specific product from the ah programs"""
    return (
        auth.ADPOperations(token, ADP_AIR_HANDLERS_RESOURCE)
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


def build_full_model_obj(session: Session, new_coil: NewAHRequest):
    model_num = new_coil.data.attributes.model_number
    adp_customer_id = new_coil.data.relationships.adp_customers.data.id
    model_w_attrs = build_model_attributes(
        session=session, model=model_num, adp_customer_id=adp_customer_id
    )
    json_api_data = dict(
        data=NewAHRObjFull(
            attributes=model_w_attrs.to_dict(),
            relationships=new_coil.data.relationships,
        ).model_dump(by_alias=True, exclude_none=True)
    )
    return json_api_data


@ah_progs.post(
    "",
    response_model=AirHandlerProgResp,
    response_model_exclude_none=True,
    response_model_exclude=RESOURCE_EXCLUSIONS,
    tags=["jsonapi"],
)
def add_to_ah_program(
    token: Token,
    session: NewSession,
    new_ah: NewAHRequest,
) -> AirHandlerProgResp:
    """create a new product in an existing program"""
    json_api_data = partial(build_full_model_obj, session, new_ah)
    adp_customer_id = new_ah.data.relationships.adp_customers.data.id
    return (
        auth.ADPOperations(token, ADP_AIR_HANDLERS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .post(
            session=session,
            data=json_api_data,
            customer_id=adp_customer_id,
        )
    )


@ah_progs.patch(
    "/{program_product_id}",
    response_model=AirHandlerProgResp,
    response_model_exclude_none=True,
    response_model_exclude=RESOURCE_EXCLUSIONS,
    tags=["jsonapi"],
)
def change_product_status(
    token: Token,
    session: NewSession,
    program_product_id: int,
    new_stage: ModStageAHReq,
) -> AirHandlerProgResp:
    adp_customer_id = new_stage.data.relationships.adp_customers.data.id
    return (
        auth.ADPOperations(token, ADP_AIR_HANDLERS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=new_stage.model_dump(by_alias=True),
            customer_id=adp_customer_id,
            obj_id=program_product_id,
        )
    )


@ah_progs.delete("/{program_product_id}", tags=["jsonapi"])
def delete_ah_program_product(
    token: Token,
    session: NewSession,
    program_product_id: int,
):
    return (
        auth.ADPOperations(token, ADP_AIR_HANDLERS_RESOURCE)
        .allow_admin()
        .delete(session=session, obj_id=program_product_id)
    )


@ah_progs.get("/{program_product_id}/" + ADP_CUSTOMERS_RESOURCE)
def get_related_customer(
    token: Token,
    session: NewSession,
    program_product_id: int,
):
    return (
        auth.ADPOperations(token, ADP_AIR_HANDLERS_RESOURCE)
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


@ah_progs.get("/{program_product_id}/relationships/" + ADP_CUSTOMERS_RESOURCE)
def get_customer_relationship(
    token: Token,
    session: NewSession,
    program_product_id: int,
):
    return (
        auth.ADPOperations(token, ADP_AIR_HANDLERS_RESOURCE)
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
