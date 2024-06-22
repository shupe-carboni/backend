from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
from app.friedrich.models import CustomerResp, CustomerQuery, CustomerQueryJSONAPI
from app.jsonapi.sqla_models import FriedrichCustomer

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_CUSTOMERS = str()

friedrich_customers = APIRouter(
    prefix=f"/{FRIEDRICH_CUSTOMERS}", tags=["friedrich", "customers"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(CustomerQueryJSONAPI)


@friedrich_customers.get(
    "", response_model=CustomerResp, response_model_exclude_none=True, tags=["jsonapi"]
)
async def friedrich_customers_collection(
    token: Token, session: NewSession, query: CustomerQuery
):
    return (
        auth.FriedrichOperations(token, FRIEDRICH_CUSTOMERS, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )
