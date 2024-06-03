"""
Customer Routes
"""

import logging
from typing import Annotated, Callable
from os import getenv
from time import sleep
from dataclasses import dataclass
from requests import get, post
from fastapi import Depends, HTTPException, status, UploadFile, Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app import auth
from app.customers.models import (
    CustomerQuery,
    CustomerResponse,
    CustomerQueryJSONAPI,
    NewCustomer,
    ModCustomer,
    CMMSSNSCustomerResults,
    NewCMMSSNSCustomer,
    CMMSSNSCustomerResp,
)
from app.db.db import SCA_DB, S3, File
from app.jsonapi.sqla_models import SCACustomer
from app.jsonapi.core_models import convert_query

CMMSSNS_URL: str = getenv("CMMSSNS_AUDIENCE")
API_TYPE = SCACustomer.__jsonapi_type_override__
customers = APIRouter(prefix=f"/{API_TYPE}", tags=["customers"])
logger = logging.getLogger("uvicorn.info")

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(CustomerQueryJSONAPI)


@dataclass
class CMMSSNSToken:
    value: str = ""

    @classmethod
    def get_token(cls, retry: int = 0) -> None:
        if retry > 2:
            raise Exception("Unable to obtain auth token from CMMSSNS API")
        if retry:
            sleep(retry)
        CMMSSNS_AUTH0 = getenv("CMMSSNS_AUTH0_DOMAIN")
        payload = {
            "client_id": getenv("CMMSSNS_CLIENT_ID"),
            "client_secret": getenv("CMMSSNS_CLIENT_SECRET"),
            "audience": CMMSSNS_URL,
            "grant_type": getenv("CMMSSNS_GRANT_TYPE"),
        }
        resp = post(CMMSSNS_AUTH0 + "/oauth/token", json=payload)
        if resp.status_code == 200:
            resp_body = resp.json()
            token_type = resp_body["token_type"]
            access_token = resp_body["access_token"]
            cls.value = f"{token_type} {access_token}"
        else:
            retry += 1
            cls.get_token(retry=retry)

    @classmethod
    def auth_header(cls) -> dict[str, str]:
        if not cls.value:
            cls.get_token()
        return {"Authorization": cls.value}


@customers.get(
    "",
    response_model=CustomerResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_collection(
    session: NewSession, token: Token, query: CustomerQuery = Depends()
) -> CustomerResponse:

    return (
        auth.CustomersOperations(token, API_TYPE)
        .allow_admin()
        .allow_sca()
        .get(session=session, query=converter(query))
    )


@customers.get("/cmmssns-customers", response_model=CMMSSNSCustomerResults)
async def cmmssns_customers(token: Token, search_term: str) -> CMMSSNSCustomerResults:
    """
    Special endpoint for querying a protected endpoint on
    another service. The intent is to allow the user to perform a
    fuzzy search for customer entities on the CMMSSNS service
    in order to avoid potential duplication.
    """
    # NOTE if this path comes after the get-resource path below,
    # that one will take over and return a typing error
    customer_perm = token.permissions
    authorized = customer_perm >= auth.Permissions.sca_employee
    if authorized:
        customers = CMMSSNS_URL + "customers"
        q_filter = f"filter={search_term.upper().strip()}"
        url = customers + f"?{q_filter}&postgres_fuzzy_match=true"
        resp = get(url=url, headers=CMMSSNSToken.auth_header())
        if resp.status_code != 200:
            raise HTTPException(resp.status_code, resp.text)
        return CMMSSNSCustomerResults(data=resp.json())
    return HTTPException(status.HTTP_401_UNAUTHORIZED)


@customers.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer(
    session: NewSession,
    token: Token,
    customer_id: int,
    query: CustomerQuery = Depends(),
) -> CustomerResponse:
    return (
        auth.CustomersOperations(token, API_TYPE)
        .allow_admin()
        .allow_sca()
        .get(
            session=session,
            query=converter(query),
            obj_id=customer_id,
        )
    )


def new_cmmssns_customer(new_customer: NewCMMSSNSCustomer) -> CMMSSNSCustomerResp:
    """
    Make a POST request to the CMMSSNS API to create a new customer
    under the Shupe Carboni Account. The token permissions are set to
    an admin scope as 'admin:shupecarboni.com',
    which means no user account is required and we don't have
    to know the user id in that service.
    """
    url = CMMSSNS_URL + "customers"
    resp = post(
        url=url, json=new_customer.model_dump(), headers=CMMSSNSToken.auth_header()
    )
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, resp.text)
    return CMMSSNSCustomerResp(**resp.json())


def get_new_cmmssns_customer_method() -> Callable:
    return new_cmmssns_customer


GetCMMSSNSCustomer = Callable[[NewCMMSSNSCustomer], CMMSSNSCustomerResp]


@customers.post(
    "",
    response_model=CustomerResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_customer(
    session: NewSession,
    token: Token,
    new_customer: NewCustomer,
    new_cmmssns_customer: GetCMMSSNSCustomer = Depends(get_new_cmmssns_customer_method),
) -> CustomerResponse:
    """
    Creates a new customer.
    If the customer exists in the CMMSSNS database,
        then use that id number.
    If the customer does not exist,
        call out to the CMMSSNS service to create
        a new customer entity and use the id returned.
    """
    create_new_entity = not bool(new_customer.data.id)
    customer_perm = token.permissions
    authorized = customer_perm >= auth.Permissions.sca_employee
    if authorized:
        if create_new_entity:
            cmmssns_customer = new_cmmssns_customer(
                new_customer=NewCMMSSNSCustomer(
                    data={"attributes": {"name": new_customer.data.attributes.name}}
                )
            )
            new_customer.data.id = cmmssns_customer.data.id
        return (
            auth.CustomersOperations(token, API_TYPE)
            .allow_admin()
            .allow_sca()
            .post(
                session=session,
                data=new_customer.model_dump(by_alias=True),
                primary_id=new_customer.data.id,
            )
        )
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)


@customers.patch(
    "/{customer_id}/customer-logo",
    response_model=CustomerResponse,
    tags=["file-upload"],
)
async def upload_customer_logo_file(
    session: NewSession, token: Token, customer_id: int, file: UploadFile
) -> CustomerResponse:
    """
    Special path with the same structure as a related object query
    but it expects a file sent as form data in the body.

    Returns the JSON:API Customer resource object, although the
        path does not accept JSON:API spec query params nor a
        resource object as part of the request.
    """
    customer_perm = token.permissions
    authorized = customer_perm >= auth.Permissions.sca_employee
    if authorized:
        new_logo = File(
            file_content=await file.read(),
            file_name=file.filename,
            file_mime=file.content_type,
        )
        file_dest = f"{API_TYPE}/{customer_id}/logo/{new_logo.file_name}"
        await S3.upload_file(file=new_logo, destination=file_dest)
        result = await mod_customer(
            session=session,
            token=token,
            primary_id=customer_id,
            mod_customer=ModCustomer(
                data={"id": customer_id, "attributes": {"logo": file_dest}}
            ),
        )
        return result
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)


@customers.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_customer(
    session: NewSession,
    token: Token,
    customer_id: int,
    mod_customer: ModCustomer,
) -> CustomerResponse:
    return (
        auth.CustomersOperations(token, API_TYPE)
        .allow_admin()
        .allow_sca()
        .patch(
            session=session,
            data=mod_customer.model_dump(exclude_none=True, by_alias=True),
            primary_id=customer_id,
            obj_id=customer_id,
        )
    )


@customers.delete("/{customer_id}", tags=["jsonapi"])
async def del_customer(session: NewSession, token: Token, customer_id: int) -> None:
    customer_perm = token.permissions
    authorized = customer_perm >= auth.Permissions.sca_admin
    if authorized:
        del_customer = """
            DELETE FROM customers
            WHERE id = :customer_id;
        """
        try:
            SCA_DB.execute(session, del_customer, {"customer_id": customer_id})
        except IntegrityError as e:
            session.rollback()
            logger.warning("Delete unsuccessful due to an integrity error.")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e)
        else:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        finally:
            session.commit()
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)
