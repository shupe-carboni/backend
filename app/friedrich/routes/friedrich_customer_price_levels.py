from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
from app.friedrich.models import (
    FriedrichCustomerPriceLevelResp,
    FriedrichCustomerPriceLevelQuery,
    FriedrichCustomerPriceLevelQueryJSONAPI,
    RelatedFriedrichCustomerResp,
    FriedrichCustomerRelResp,
    NewFriedrichCustomerPriceLevel,
)
from app.jsonapi.sqla_models import FriedrichCustomerPriceLevel

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_CUSTOMER_PRICE_LEVELS = FriedrichCustomerPriceLevel.__jsonapi_type_override__

friedrich_customer_price_levels = APIRouter(
    prefix=f"/{FRIEDRICH_CUSTOMER_PRICE_LEVELS}",
    tags=["friedrich", "pricing-reference"],
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
    token: Token,
    session: NewSession,
    query: FriedrichCustomerPriceLevelQuery = Depends(),
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
    "/{friedrich_customer_price_level_id}/friedrich-customers",
    response_model=RelatedFriedrichCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_price_level_related_friedrich_customers(
    token: Token,
    session: NewSession,
    friedrich_customer_price_level_id: int,
    query: FriedrichCustomerPriceLevelQuery = Depends(),
) -> RelatedFriedrichCustomerResp:
    return (
        auth.FriedrichOperations(token, FriedrichCustomerPriceLevel, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_customer_price_level_id,
            "friedrich-customers",
        )
    )


@friedrich_customer_price_levels.get(
    "/{friedrich_customer_price_level_id}/relationships/friedrich-customers",
    response_model=FriedrichCustomerRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_price_level_relationships_freidrich_customers(
    token: Token,
    session: NewSession,
    friedrich_customer_price_level_id: int,
    query: FriedrichCustomerPriceLevelQuery = Depends(),
) -> FriedrichCustomerRelResp:
    return (
        auth.FriedrichOperations(token, FriedrichCustomerPriceLevel, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_customer_price_level_id,
            "friedrich-customers",
            True,
        )
    )


@friedrich_customer_price_levels.post(
    "",
    response_model=FriedrichCustomerPriceLevelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_friedrich_customer_price_level(
    token: Token,
    session: NewSession,
    mod_data: NewFriedrichCustomerPriceLevel,
) -> FriedrichCustomerPriceLevelResp:
    return (
        auth.FriedrichOperations(token, FriedrichCustomerPriceLevel, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            primary_id=mod_data.data.relationships.friedrich_customers.data.id,
        )
    )


from app.friedrich.models import ModFriedrichCustomerPriceLevel


@friedrich_customer_price_levels.patch(
    "/{friedrich_customer_price_level_id}",
    response_model=FriedrichCustomerPriceLevelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_friedrich_customer_price_level(
    token: Token,
    session: NewSession,
    friedrich_customer_price_level_id: int,
    mod_data: ModFriedrichCustomerPriceLevel,
) -> FriedrichCustomerPriceLevelResp:
    return (
        auth.FriedrichOperations(token, FriedrichCustomerPriceLevel, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=friedrich_customer_price_level_id,
            primary_id=mod_data.data.relationships.friedrich_customers.data.id,
        )
    )


@friedrich_customer_price_levels.delete(
    "/{friedrich_customer_price_level_id}",
    tags=["jsonapi"],
)
async def del_friedrich_customer_price_level(
    token: Token,
    session: NewSession,
    friedrich_customer_price_level_id: int,
    friedrich_customer_id: int,
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichCustomerPriceLevel, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session,
            obj_id=friedrich_customer_price_level_id,
            primary_id=friedrich_customer_id,
        )
    )
