from typing import Annotated
from fastapi import Depends, BackgroundTasks
from fastapi.routing import APIRouter
from functools import partial
from logging import getLogger

from app import auth
from app.db import Session, ADP_DB, Stage
from app.adp.models import (
    AirHandlerProgResp,
    AirHandlerProgQuery,
    AHProgQueryJSONAPI,
    NewAHRequest,
    ModStageAHReq,
    NewAHRObjFull,
)
from app.adp.extraction.models import build_model_attributes, ParsingModes
from app.jsonapi.sqla_models import ADPAHProgram, ADPCustomer
from app.jsonapi.core_models import convert_query
from app.jsonapi.sqla_jsonapi_ext import MAX_PAGE_SIZE

logger = getLogger("uvicorn.info")

PARENT_PREFIX = "/vendors/adp"
ADP_AIR_HANDLERS_RESOURCE = ADPAHProgram.__jsonapi_type_override__
ADP_CUSTOMERS_RESOURCE = ADPCustomer.__jsonapi_type_override__
ah_progs = APIRouter(
    prefix=f"/{ADP_AIR_HANDLERS_RESOURCE}", tags=["air handlers", "adp"]
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


def background_stage_update(
    token: auth.VerifiedToken,
    session: Session,
    updated_model: AirHandlerProgResp,
    adp_customer_id: int,
) -> None:
    """when a AH is set to ACTIVE stage, any other record for the customer
    with the same model number and ACTIVE is updated to REMOVED"""
    model_number_updated = updated_model.data.attributes.model_number

    other_ids_to_update = [
        resource_obj["id"]
        for resource_obj in all_ah_programs(
            token,
            session,
            AirHandlerProgQuery(
                filter_model_number=model_number_updated, include="adp-customers"
            ),
        )["data"]
        if (
            resource_obj["relationships"]["adp-customers"]["data"]["id"]
            == adp_customer_id
        )
        and (resource_obj["attributes"]["stage"] == "active")
        and (resource_obj["id"] != updated_model.data.id)
    ]
    if not other_ids_to_update:
        logger.info("No AH status to update")
    for id_ in other_ids_to_update:
        new_stage = ModStageAHReq(
            data={
                "id": id_,
                "type": ADP_AIR_HANDLERS_RESOURCE,
                "attributes": {"stage": Stage.REMOVED},
                "relationships": {
                    "adp-customers": {
                        "data": {
                            "id": adp_customer_id,
                            "type": ADP_CUSTOMERS_RESOURCE,
                        }
                    }
                },
            }
        )
        try:
            (
                auth.ADPOperations(token, ADPAHProgram, prefix=PARENT_PREFIX)
                .allow_admin()
                .allow_sca()
                .allow_dev()
                .allow_customer("std")
                .patch(
                    session=session,
                    data=new_stage.model_dump(exclude_none=True, by_alias=True),
                    primary_id=adp_customer_id,
                    obj_id=id_,
                )
            )
        except Exception:
            logger.warning(f"Failed to update status of AH with id {id_}")
        else:
            logger.info(f"Successfully updated AH with {id_} to stage = 'REMOVED'")


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
        auth.ADPOperations(token, ADPAHProgram, prefix=PARENT_PREFIX)
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
        auth.ADPOperations(token, ADPAHProgram, prefix=PARENT_PREFIX)
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


def build_full_model_obj(session: Session, new_coil: NewAHRequest, token: Token):
    match auth.Permissions(token.permissions):
        case auth.Permissions.developer:
            parse_mode = ParsingModes.DEVELOPER
        case _:
            parse_mode = ParsingModes.CUSTOMER_PRICING
    model_num = new_coil.data.attributes.model_number
    adp_customer_id = new_coil.data.relationships.adp_customers.data.id
    model_w_attrs = build_model_attributes(
        session=session,
        model=model_num,
        adp_customer_id=adp_customer_id,
        parse_mode=parse_mode,
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
    json_api_data = partial(build_full_model_obj, session, new_ah, token)
    adp_customer_id = new_ah.data.relationships.adp_customers.data.id
    return (
        auth.ADPOperations(token, ADPAHProgram, prefix=PARENT_PREFIX)
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
    bg_tasks: BackgroundTasks,
) -> AirHandlerProgResp:
    adp_customer_id = new_stage.data.relationships.adp_customers.data.id
    set_other_active_models_to_removed = new_stage.data.attributes.stage == Stage.ACTIVE
    updated_model = AirHandlerProgResp(
        **auth.ADPOperations(token, ADPAHProgram, prefix=PARENT_PREFIX)
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
    if set_other_active_models_to_removed:
        bg_tasks.add_task(
            background_stage_update, token, session, updated_model, adp_customer_id
        )
    return updated_model


@ah_progs.delete("/{program_product_id}", tags=["jsonapi"])
def delete_ah_program_product(
    token: Token, session: NewSession, program_product_id: int, adp_customer_id: int
):
    return (
        auth.ADPOperations(token, ADPAHProgram, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session=session, obj_id=program_product_id, primary_id=adp_customer_id)
    )


@ah_progs.get("/{program_product_id}/" + ADP_CUSTOMERS_RESOURCE)
def get_related_customer(
    token: Token,
    session: NewSession,
    program_product_id: int,
):
    return (
        auth.ADPOperations(token, ADPAHProgram, prefix=PARENT_PREFIX)
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
        auth.ADPOperations(token, ADPAHProgram, prefix=PARENT_PREFIX)
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
