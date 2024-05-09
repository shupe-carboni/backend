from typing import Annotated
from os import getenv
from time import sleep
from dataclasses import dataclass
from requests import get, post, patch, delete
from fastapi import Depends, HTTPException, status, UploadFile
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app import auth
from app.customers.models import (
    CustomerQuery, CustomerResponse, CustomerQueryJSONAPI,
    NewCustomer, ModCustomer, CMMSSNSCustomers
)
from app.db.db import SCA_DB, S3, File
from app.jsonapi.sqla_models import SCACustomer, serializer
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
    value: str=''

    @classmethod
    def get_token(cls, retry: int=0) -> None:
        if retry > 2:
            raise Exception('Unable to obtain auth token from CMMSSNS API')
        if retry:
            sleep(retry)
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
        '/cmmssns-customers',
        response_model=CMMSSNSCustomers
    )
async def cmmssns_customers(
        token: CustomersPerm,
        search_term: str
    ) -> CMMSSNSCustomers:
    """
        Special endpoint for querying a protected endpoint on 
        another service. The intent is to allow the user to perform a 
        fuzzy search for customer entities on the CMMSSNS service 
        in order to avoid potential duplication.
    """
    # NOTE if this path comes after the get-resource path below, 
    # that one will take over and return a typing error
    customer_perm = token.permissions.get('customers')
    authorized = customer_perm >= auth.CustomersPermPriority.sca_employee
    if authorized:
        customers = CMMSSNS_URL + 'customers'
        q_filter = f'filter={search_term.upper().strip()}'
        url = customers + f'?{q_filter}&postgres_fuzzy_match=true'
        resp = get(url=url, headers=CMMSSNSToken.auth_header())
        if resp.status_code != 200:
            raise HTTPException(resp.status_code, resp.text)
        return CMMSSNSCustomers(data=resp.json())
    return HTTPException(status.HTTP_401_UNAUTHORIZED)

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
        send back or generate a customer id. (HALF DONE)
    2. When creating a new customer loction, POST that to the CMMSSNS
        application.
        - if CMMSSNS creates a new branch, should it be sent down or
        is it on this application to check for it first?
    3. For each applicable vendor, make a record in respective
        customer tables for those vendors as well as mapping tables to 
        branches (at least one).
    4. Add ancillary required records (i.e. customer payment tems, 
      logo file, special prepaid frieght terms, etc.)
    5. If files are required (i.e. images), upload them. (DONE)
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
    """
        Creates a new customer.
        If the customer exists in the CMMSSNS database,
            then use that id number.
        If the customer does not exist, 
            call out to the CMMSSNS service to create
            a new customer entity and use the id returned.
    """
    customer_perm = token.permissions.get('customers')
    authorized = customer_perm >= auth.CustomersPermPriority.sca_employee
    if authorized:
        ...
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)

@customers.patch(
        '/{customer_id}/customer-logo',
        response_model=CustomerResponse,
        tags=['file-upload']
    )
async def upload_customer_logo_file(
        session: NewSession,
        token: CustomersPerm,
        customer_id: int,
        file: UploadFile
    ) -> CustomerResponse:
    """
        Special path with the same structure as a related object query
        but it expects a file sent as form data in the body.

        Returns the JSON:API Customer resource object, although the
            path does not accept JSON:API spec query params nor a
            resource object as part of the request.
    """
    customer_perm = token.permissions.get('customers')
    authorized = customer_perm >= auth.CustomersPermPriority.sca_employee
    if authorized:
        new_logo = File(
            file_content=await file.read(),
            file_name=file.filename,
            file_mime=file.content_type
        )
        file_dest = f'{API_TYPE}/{customer_id}/logo/{new_logo.file_name}'
        await S3.upload_file(file=new_logo, destination=file_dest)
        result = await mod_customer(
            session=session,
            token=token,
            customer_id=customer_id,
            mod_customer=ModCustomer(
                data={
                    'id': customer_id,
                    'attributes': {
                        'logo': file_dest
                    }
                }
            )
        )
        return result
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)

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
    customer_perm = token.permissions.get('customers')
    if customer_perm >= auth.CustomersPermPriority.sca_employee:
        result = serializer.patch_resource(
            session=session,
            json_data=mod_customer.model_dump(),
            api_type=API_TYPE,
            obj_id=customer_id
        )
        return result.data
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)

@customers.delete('/{customer_id}',tags=['jsonapi'])
async def del_customer(
        session: NewSession,
        token: CustomersPerm,
        customer_id: int
    ) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)