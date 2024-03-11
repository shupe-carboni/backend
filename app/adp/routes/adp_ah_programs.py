from typing import Annotated
from fastapi import HTTPException, Depends, status
from fastapi.routing import APIRouter
from sqlalchemy_jsonapi.errors import ResourceNotFoundError

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
        query: AirHandlerProgQuery=Depends(),   # type: ignore
    ) -> AirHandlerProgResp:
    """List out all ah programs.
        An SCA admin or employee will see all programs that exist.
        A customer will see only their own programs"""
    if not token.email_verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    adp_perm = token.permissions.get('adp')
    if adp_perm >= auth.ADPPermPriority.sca_employee:
        return serializer.get_collection(session, query, ADP_AIR_HANDLERS_RESOURCE)
    elif adp_perm >= auth.ADPPermPriority.customer_std:
        ids = ADP_DB.get_permitted_customer_location_ids(
            session=session,
            email_address=token.email,
            select_type=adp_perm.name,
        )
        return serializer.get_collection(session, query, ADP_AIR_HANDLERS_RESOURCE, ids)
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)

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
        query: AirHandlerProgQuery=Depends(),   # type: ignore
    ) -> AirHandlerProgResp:
    """get a specific product from the ah programs"""
    if not token.email_verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    adp_perm = token.permissions.get('adp')
    if adp_perm >= auth.ADPPermPriority.sca_employee:
        return serializer.get_resource(
            session=session,
            query=query,
            api_type=ADP_AIR_HANDLERS_RESOURCE,
            obj_id=program_product_id,
            obj_only=True
        )
    elif adp_perm >= auth.ADPPermPriority.customer_std:
        ids = ADP_DB.get_permitted_customer_location_ids(
            session=session,
            email_address=token.email,
            select_type=adp_perm.name
        )
        try:
            return serializer.get_resource(
                session=session,
                query=query,
                api_type=ADP_AIR_HANDLERS_RESOURCE,
                obj_id=program_product_id,
                obj_only=True,
                permitted_ids=ids
            )
        except ResourceNotFoundError:
            raise HTTPException(status.HTTP_204_NO_CONTENT)
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)

@ah_progs.post('/{adp_customer_id}', tags=['jsonapi'])
def add_to_ah_program(
        token: ADPPerm,
        session: NewSession,
        adp_customer_id: int,
        new_ah: NewAHRObj,
    ):
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
