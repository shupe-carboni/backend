from typing import Annotated
from fastapi import HTTPException, Depends, status
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB 
from app.adp.main import add_model_to_program
from app.adp.models import (
    CoilProgQuery,
    CoilProgQueryJSONAPI,
    CoilProgResp,
    NewCoilRObj,
    ModStageCoilReq
)
from app.jsonapi.sqla_models import serializer, ADPCoilProgram

ADP_COILS_RESOURCE = ADPCoilProgram.__jsonapi_type_override__
ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_perms_present)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]

coil_progs = APIRouter(prefix=f'/{ADP_COILS_RESOURCE}', tags=['coils','programs'])

def convert_query(query: CoilProgQuery) -> CoilProgQueryJSONAPI:
    return CoilProgQueryJSONAPI(**query.model_dump(exclude_none=True)).model_dump(by_alias=True, exclude_none=True)

@coil_progs.get(
        '',
        response_model=CoilProgResp,
        response_model_exclude_none=True,
        tags=['jsonapi']
)
def all_coil_programs(
        token: ADPPerm,
        session: NewSession,
        query: CoilProgQuery=Depends()
    ) -> CoilProgResp:
    """List out all coil programs.
        An SCA admin or employee will see all programs that exist.
        A customer will see only their own programs"""
    return auth.secured_get_query(
        db=ADP_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['adp'],
        resource=ADP_COILS_RESOURCE,
        query=convert_query(query)
    )


@coil_progs.get(
        '/{program_product_id}',
        response_model=CoilProgResp,
        response_model_exclude_none=True,
        tags=['jsonapi']
)
def coil_program_product(
        token: ADPPerm,
        session: NewSession,
        program_product_id: int,
        query: CoilProgQuery=Depends()
    ) -> CoilProgResp:
    """get a specific product from the coil programs"""
    return auth.secured_get_query(
        db=ADP_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['adp'],
        resource=ADP_COILS_RESOURCE,
        query=convert_query(query),
        obj_id=program_product_id
    )

@coil_progs.post(
        '/{adp_customer_id}',
        response_model=CoilProgResp,
        response_model_exclude_none=True,
        tags=['jsonapi']
)
def add_to_coil_program(
        token: ADPPerm,
        session: NewSession,
        adp_customer_id: int,
        new_coil: NewCoilRObj
    ) -> CoilProgResp:
    """add coil product for a customer"""
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        model_num = new_coil.attributes.model_number
        new_id = add_model_to_program(session=session, model=model_num, adp_customer_id=adp_customer_id)
        return serializer.get_resource(
            session=session,
            query=convert_query(CoilProgQuery()),
            api_type=ADP_COILS_RESOURCE,
            obj_id=new_id,
            obj_only=True,
            permitted_ids=None
        )
    else:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@coil_progs.patch(
        '/{adp_customer_id}',
        response_model=CoilProgResp,
        response_model_exclude_none=True,
        tags=['jsonapi']
)
def change_product_status(
        token: ADPPerm,
        session: NewSession,
        adp_customer_id: int,
        new_stage: ModStageCoilReq
    ) -> CoilProgResp:
    """change the stage of a program coil
        Stage: ACITVE, PROPOSED, REJECTED, REMOVED
        examples:
            PROPOSED -> ACTIVE
            ACTIVE -> REMOVED
    """
    associated_ids = ADP_DB.load_df(session, 'coil_programs', adp_customer_id, id_only=True).id.to_list()
    if new_stage.data.id not in associated_ids or not associated_ids:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Customer ID {adp_customer_id} is not associated with product id {new_stage.id}")
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        result = serializer.patch_resource(session=session, json_data=new_stage.model_dump(), api_type=ADP_COILS_RESOURCE, obj_id=new_stage.data.id)
        return result.data
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@coil_progs.delete('/{program_product_id}')
def permanently_delete_record(
        token: ADPPerm,
        session: NewSession,
        program_product_id: int,
    ) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@coil_progs.get(
        '/{program_product_id}/adp-customers'
)
def get_related_customer(
        token: ADPPerm,
        session: NewSession,
        program_product_id: int,
    ):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)