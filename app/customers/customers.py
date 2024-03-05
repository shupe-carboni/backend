from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app import auth
from app.customers.models import CustomerQuery, CustomerResponse
from app.db.db import SCA_DB
from app.jsonapi.sqla_models import serializer

api_type = 'customers'
customers = APIRouter(prefix=f'/{api_type}', tags=['customers'])

CustomersPerm = Annotated[auth.VerifiedToken, Depends(auth.customers_perms_present)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]

@customers.get('', response_model=CustomerResponse, response_model_exclude_none=True)
async def customer_collection(
        session: NewSession,
        token: CustomersPerm,
        query: CustomerQuery=Depends(), # type: ignore
    ) -> CustomerResponse:
    return serializer.get_collection(session=session, query=query, api_type=api_type,user_id=0)

@customers.get('/{customer_id}', response_model=CustomerResponse, response_model_exclude_none=True)
async def customer(
        session: NewSession,
        token: CustomersPerm,
        customer_id: int,
        query: CustomerQuery=Depends(), # type: ignore
    ) -> CustomerResponse:
    return serializer.get_resource(session=session, query=query, api_type=api_type, obj_id=customer_id, obj_only=True)