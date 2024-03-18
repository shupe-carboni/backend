from typing import Annotated
from fastapi import HTTPException, Depends, status
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.adp.main import add_model_to_program
from app.adp.models import (
    AirHandlerProgResp,
    AirHandlerProgQuery,
    NewAHRObj
)
from app.jsonapi.sqla_models import serializer, ADPAHProgram

ADP_AIR_HANDLERS_RESOURCE = ADPAHProgram.__jsonapi_type_override__
ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_perms_present)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]

ah_progs = APIRouter(prefix=f'/{ADP_AIR_HANDLERS_RESOURCE}', tags=['air handlers','programs'])

@ah_progs.get(
        '',
        response_model=AirHandlerProgResp,
        response_model_exclude_none=True,
        tags=['jsonapi']
)
def all_ah_programs(
        token: ADPPerm,
        session: NewSession,
        query: AirHandlerProgQuery=Depends()
    ) -> AirHandlerProgResp:
    """List out all ah programs.
        An SCA admin or employee will see all programs that exist.
        A customer will see only their own programs"""
    return auth.secured_get_query(
        db=ADP_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['adp'],
        resource=ADP_AIR_HANDLERS_RESOURCE,
        query=query
    )

@ah_progs.get(
        '/{program_product_id}',
        response_model=AirHandlerProgResp,
        response_model_exclude_none=True,
        tags=['jsonapi']
)
def ah_program_product(
        session: NewSession,
        token: ADPPerm,
        program_product_id: int,
        query: AirHandlerProgQuery=Depends()
    ) -> AirHandlerProgResp:
    """get a specific product from the ah programs"""
    return auth.secured_get_query(
        db=ADP_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['adp'],
        resource=ADP_AIR_HANDLERS_RESOURCE,
        query=query,
        obj_id=program_product_id
    )

@ah_progs.post('/{adp_customer_id}', tags=['jsonapi'])
def add_to_ah_program(
        token: ADPPerm,
        session: NewSession,
        adp_customer_id: int,
        new_ah: NewAHRObj,
    ) -> AirHandlerProgResp:
    """create a new product in an existing program"""
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        model_num = new_ah.attributes.model_number
        new_id = add_model_to_program(session=session, model=model_num, adp_customer_id=adp_customer_id)
        return serializer.get_resource(
            session=session,
            query=AirHandlerProgQuery(),
            api_type=ADP_AIR_HANDLERS_RESOURCE,
            obj_id=new_id,
            obj_only=True,
            permitted_ids=None
        )
    else:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
