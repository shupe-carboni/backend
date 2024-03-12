from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app import auth
from app.customers.models import CustomerQuery, CustomerResponse
from app.db.db import SCA_DB
from app.jsonapi.sqla_models import serializer, SCACustomer

api_type = SCACustomer.__jsonapi_type_override__
customers = APIRouter(prefix=f'/{api_type}', tags=['customers'])

CustomersPerm = Annotated[auth.VerifiedToken, Depends(auth.customers_perms_present)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]

@customers.get('', response_model=CustomerResponse, response_model_exclude_none=True)
async def customer_collection(
        session: NewSession,
        token: CustomersPerm,
        query: CustomerQuery=Depends(), # type: ignore
    ) -> CustomerResponse:
    return auth.secured_get_query(
        db=SCA_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['customers'],
        resource=api_type,
        query=query
    )

@customers.get('/{customer_id}', response_model=CustomerResponse, response_model_exclude_none=True)
async def customer(
        session: NewSession,
        token: CustomersPerm,
        customer_id: int,
        query: CustomerQuery=Depends(), # type: ignore
    ) -> CustomerResponse:
    return auth.secured_get_query(
        db=SCA_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['customers'],
        resource=api_type,
        query=query,
        obj_id=customer_id
    )