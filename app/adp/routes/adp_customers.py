from typing import Annotated
from fastapi import HTTPException, Depends, status
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB 
from app.adp.models import (
    CustomersResp,
    CustomersQuery,
    CustomersQueryJSONAPI 
)
from app.jsonapi.sqla_models import serializer, ADPCustomer

ADP_CUSTOMERS = ADPCustomer.__jsonapi_type_override__
ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_perms_present)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]

adp_customers = APIRouter(prefix=f'/{ADP_CUSTOMERS}', tags=['customers'])

def convert_query(query: CustomersQuery) -> dict[str,str]:
    return CustomersQueryJSONAPI(**query.model_dump(exclude_none=True)).model_dump(by_alias=True, exclude_none=True)

@adp_customers.get(
        '',
        response_model=CustomersResp,
        response_model_exclude_none=True,
        tags=['jsonapi']
)
def all_adp_customers(
        token: ADPPerm,
        session: NewSession,
        query: CustomersQuery=Depends()
    ) -> CustomersResp:
    # ):
    """List out all coil programs.
        An SCA admin or employee will see all programs that exist.
        A customer will see only their own programs"""
    return auth.secured_get_query(
        db=ADP_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['adp'],
        resource=ADP_CUSTOMERS,
        query=convert_query(query)
    )

@adp_customers.get(
        '/{customer_id}',
        response_model=CustomersResp,
        response_model_exclude_none=True,
        tags=['jsonapi']
)
def coil_program_product(
        token: ADPPerm,
        session: NewSession,
        program_product_id: int,
        query: CustomersQuery=Depends()
    ) -> CustomersResp:
    """get a specific product from the coil programs"""
    return auth.secured_get_query(
        db=ADP_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['adp'],
        resource=ADP_CUSTOMERS,
        query=convert_query(query),
        obj_id=program_product_id
    )