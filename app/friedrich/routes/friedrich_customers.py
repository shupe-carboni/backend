
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.friedrich.models import (
    FriedrichCustomerResp,
    FriedrichCustomerQuery,
    FriedrichCustomerQueryJSONAPI,
)
from app.jsonapi.sqla_models import FriedrichCustomer

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_CUSTOMERS = FriedrichCustomer.__jsonapi_type_override__

friedrich_customers = APIRouter(
    prefix=f"/{FRIEDRICH_CUSTOMERS}", tags=["friedrich", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(FriedrichCustomerQueryJSONAPI)


@friedrich_customers.get(
    "",
    response_model=FriedrichCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_collection(
    token: Token, session: NewSession, query: FriedrichCustomerQuery
) -> FriedrichCustomerResp:
    return (
        auth.FriedrichOperations(token, FriedrichCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@friedrich_customers.get(
    "/{friedrich_customer_id}",
    response_model=FriedrichCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_resource(
    token: Token,
    session: NewSession,
    query: FriedrichCustomerQuery,
    friedrich_customer_id: int,
) -> FriedrichCustomerResp:
    return (
        auth.FriedrichOperations(token, FriedrichCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_customer_id)
    )


@friedrich_customers.get(
    "/{friedrich_customer_id}/RELATED_RESOURCE",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_related_RELATED_RESOURCE(
    token: Token,
    session: NewSession,
    query: FriedrichCustomerQuery,
    friedrich_customer_id: int,
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_customer_id, "RELATED_RESOURCE")
    )


@friedrich_customers.get(
    "/{friedrich_customer_id}/relationships/RELATED_RESOURCE",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_relationships_RELATED_RESOURCE(
    token: Token,
    session: NewSession,
    query: FriedrichCustomerQuery,
    friedrich_customer_id: int,
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_customer_id, "RELATED_RESOURCE", True)
    )

    