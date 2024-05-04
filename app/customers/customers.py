from typing import Annotated
from os import getenv
from time import sleep
from dataclasses import dataclass
from requests import get, post, patch, delete
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app import auth
from app.customers.models import (
    CustomerQuery, CustomerResponse, CustomerQueryJSONAPI,
    NewCustomer, ModCustomer
)
from app.db.db import SCA_DB
from app.jsonapi.sqla_models import SCACustomer
from app.jsonapi.core_models import convert_query

API_TYPE = SCACustomer.__jsonapi_type_override__
customers = APIRouter(prefix=f'/{API_TYPE}', tags=['customers'])

CMMSSNS_URL: str = getenv('CMMSSNS_AUDIENCE')

CustomersPerm = Annotated[
    auth.VerifiedToken,
    Depends(auth.customers_perms_present)
]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(CustomerQueryJSONAPI)

@dataclass
class CMMSSNSToken:
    value: str

    @classmethod
    def get_token(cls, retry: int=0) -> None:
        if retry > 2:
            raise Exception('Unable to obtain auth token from CMMSSNS API')
        CMMSSNS_AUTH0 = getenv('CMMSSNS_AUTH0_DOMAIN')
        payload = {
            'client_id': getenv('CMMSSNS_CLIENT_ID'),
            'client_secret': getenv('CMMSSNS_CLIENT_SECRET'),
            'audience': CMMSSNS_URL,
            'grant_type': getenv('CMMSSNS_GRANT_TYPE')
        }
        resp = post(CMMSSNS_AUTH0+'/oauth/token', json=payload)
        if resp.status_code == 200:
            resp_body = resp.json()
            token_type = resp_body['token_type']
            access_token = resp_body['access_token']
            cls.value = f"{token_type} {access_token}"
        else:
            retry += 1
            cls.get_token(retry=retry)
    
    @classmethod
    def auth_header(cls) -> dict[str,str]:
        if not cls.value:
            cls.get_token()
        return {'Authorization': cls.value}

@customers.get(
        '',
        response_model=CustomerResponse,
        response_model_exclude_none=True,
        tags=['jsonapi']
    )
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

@customers.get(
        '/{customer_id}',
        response_model=CustomerResponse,
        response_model_exclude_none=True,
        tags=['jsonapi']
    )
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

# TODO
"""
    1. when a customer is added, call out to the CMMSSNS API to either 
        send back or generate a customer id.
    2. When creating a new customer loction, POST that to the CMMSSNS
        application.
        - if CMMSSNS creates a new branch, should it be sent down or
        is it on this application to check for it first?
    3. For each applicable vendor, make a record in respective
        customer tables for those vendors as well as mapping tables to 
        branches (at least one).
    4. Add ancillary required records (i.e. customer payment tems, 
      logo file, special prepaid frieght terms, etc.)
    5. If files are required (i.e. images), upload them.
"""
@customers.post(
        '',
        response_model=CustomerResponse,
        response_model_exclude_none=True,
        tags=['jsonapi']
    )
async def new_customer(
        session: NewSession,
        token: CustomersPerm,
        new_customer: NewCustomer
    ) -> CustomerResponse:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@customers.patch(
        '/{customer_id}',
        response_model=CustomerResponse,
        response_model_exclude_none=True,
        tags=['jsonapi']
    )
async def mod_customer(
        session: NewSession,
        token: CustomersPerm,
        customer_id: int,
        mod_customer: ModCustomer
    ) -> CustomerResponse:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@customers.delete('/{customer_id}',tags=['jsonapi'])
async def del_customer(
        session: NewSession,
        token: CustomersPerm,
        customer_id: int
    ) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)