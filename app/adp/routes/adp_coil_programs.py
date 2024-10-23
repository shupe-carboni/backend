from typing import Annotated
from functools import partial
from fastapi import Depends, BackgroundTasks
from fastapi.routing import APIRouter
from logging import getLogger

from app import auth
from app.db import Session, ADP_DB, Stage
from app.adp.extraction.models import build_model_attributes, ParsingModes
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

logger = getLogger("uvicorn.info")

PARENT_PREFIX = "/vendors/adp"
ADP_COILS_RESOURCE = ADPCoilProgram.__jsonapi_type_override__
ADP_CUSTOMERS_RESOURCE = ADPCustomer.__jsonapi_type_override__
coil_progs = APIRouter(prefix=f"/{ADP_COILS_RESOURCE}", tags=["coils", "adp"])

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


def background_stage_update(
    token: auth.VerifiedToken,
    session: Session,
    updated_model: CoilProgResp,
    adp_customer_id: int,
) -> None:
    """when a coil is set to ACTIVE stage, any other record for the customer
    with the same model number and ACTIVE is updated to REMOVED"""
    model_number_updated = updated_model.data.attributes.model_number

    other_ids_to_update = [
        resource_obj["id"]
        for resource_obj in all_coil_programs(
            token,
            session,
            CoilProgQuery(
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
        logger.info("No coil status to update")
    for id_ in other_ids_to_update:
        new_stage = ModStageCoilReq(
            data={
                "id": id_,
                "type": ADP_COILS_RESOURCE,
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
                auth.ADPOperations(token, ADPCoilProgram, prefix=PARENT_PREFIX)
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
            logger.info(f"Failed to update status of coil with id {id_}")
        else:
            logger.info(f"Successfully updated coil with {id_} to stage = 'REMOVED'")


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
        auth.ADPOperations(token, ADPCoilProgram, prefix=PARENT_PREFIX)
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
        auth.ADPOperations(token, ADPCoilProgram, prefix=PARENT_PREFIX)
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


def build_full_model_obj(session: Session, new_coil: NewCoilRequest, token: Token):
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
    json_api_data = partial(build_full_model_obj, session, new_coil, token)
    adp_customer_id = new_coil.data.relationships.adp_customers.data.id
    return (
        auth.ADPOperations(token, ADPCoilProgram, prefix=PARENT_PREFIX)
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
    bg_tasks: BackgroundTasks,
) -> CoilProgResp:
    """change the stage of a program coil
    Stage: ACITVE, PROPOSED, REJECTED, REMOVED
    examples:
        PROPOSED -> ACTIVE
        ACTIVE -> REMOVED
    """
    adp_customer_id = new_stage.data.relationships.adp_customers.data.id
    set_other_active_models_to_removed = new_stage.data.attributes.stage == Stage.ACTIVE
    updated_model = CoilProgResp(
        **auth.ADPOperations(token, ADPCoilProgram, prefix=PARENT_PREFIX)
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


@coil_progs.delete("/{program_product_id}", tags=["jsonapi"])
def permanently_delete_record(
    token: Token, session: NewSession, program_product_id: int, adp_customer_id: int
) -> None:
    return (
        auth.ADPOperations(token, ADPCoilProgram, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, program_product_id, adp_customer_id, hard_delete=True)
    )


@coil_progs.get("/{program_product_id}/" + ADP_CUSTOMERS_RESOURCE)
def get_related_customer(
    token: Token,
    session: NewSession,
    program_product_id: int,
):
    return (
        auth.ADPOperations(token, ADPCoilProgram)
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
        auth.ADPOperations(token, ADPCoilProgram, prefix=PARENT_PREFIX)
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
