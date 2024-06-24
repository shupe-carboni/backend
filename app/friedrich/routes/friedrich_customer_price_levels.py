
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.friedrich.models import (
    FriedrichCustomerPriceLevelResp,
    FriedrichCustomerPriceLevelQuery,
    FriedrichCustomerPriceLevelQueryJSONAPI,
)
from app.jsonapi.sqla_models import FriedrichCustomerPriceLevel

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_CUSTOMER_PRICE_LEVELS = FriedrichCustomerPriceLevel.__jsonapi_type_override__

friedrich_customer_price_levels = APIRouter(
    prefix=f"/{FRIEDRICH_CUSTOMER_PRICE_LEVELS}", tags=["friedrich", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(FriedrichCustomerPriceLevelQueryJSONAPI)


@friedrich_customer_price_levels.get(
    "",
    response_model=FriedrichCustomerPriceLevelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_price_level_collection(
    token: Token, session: NewSession, query: FriedrichCustomerPriceLevelQuery = Depends()
) -> FriedrichCustomerPriceLevelResp:
    return (
        auth.FriedrichOperations(token, FriedrichCustomerPriceLevel, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@friedrich_customer_price_levels.get(
    "/{friedrich_customer_price_level_id}",
    response_model=FriedrichCustomerPriceLevelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_price_level_resource(
    token: Token,
    session: NewSession,
    friedrich_customer_price_level_id: int,
    query: FriedrichCustomerPriceLevelQuery = Depends(),
) -> FriedrichCustomerPriceLevelResp:
    return (
        auth.FriedrichOperations(token, FriedrichCustomerPriceLevel, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_customer_price_level_id)
    )


@friedrich_customer_price_levels.get(
    "/{friedrich_customer_price_level_id}/RELATED_RESOURCE",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_price_level_related_RELATED_RESOURCE(
    token: Token,
    session: NewSession,
    friedrich_customer_price_level_id: int,
    query: FriedrichCustomerPriceLevelQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichCustomerPriceLevel, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_customer_price_level_id, "RELATED_RESOURCE")
    )


@friedrich_customer_price_levels.get(
    "/{friedrich_customer_price_level_id}/relationships/RELATED_RESOURCE",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_price_level_relationships_RELATED_RESOURCE(
    token: Token,
    session: NewSession,
    friedrich_customer_price_level_id: int,
    query: FriedrichCustomerPriceLevelQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichCustomerPriceLevel, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_customer_price_level_id, "RELATED_RESOURCE", True)
    )

    