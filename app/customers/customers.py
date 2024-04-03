from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app import auth
from app.customers.models import CustomerQuery, CustomerResponse, CustomerQueryJSONAPI
from app.db.db import SCA_DB
from app.jsonapi.sqla_models import SCACustomer
from app.jsonapi.core_models import convert_query

API_TYPE = SCACustomer.__jsonapi_type_override__
customers = APIRouter(prefix=f'/{API_TYPE}', tags=['customers'])

CustomersPerm = Annotated[auth.VerifiedToken, Depends(auth.customers_perms_present)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(CustomerQueryJSONAPI)

@customers.get('', response_model=CustomerResponse, response_model_exclude_none=True)
async def customer_collection(
        session: NewSession,
        token: CustomersPerm,
        query: CustomerQuery=Depends()
    ) -> CustomerResponse:

    return auth.secured_get_query(
        db=SCA_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['customers'],
        resource=API_TYPE,
        query=converter(query)
    )

@customers.get('/{customer_id}', response_model=CustomerResponse, response_model_exclude_none=True)
async def customer(
        session: NewSession,
        token: CustomersPerm,
        customer_id: int,
        query: CustomerQuery=Depends()
    ) -> CustomerResponse:
    return auth.secured_get_query(
        db=SCA_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['customers'],
        resource=API_TYPE,
        query=converter(query),
        obj_id=customer_id
    )