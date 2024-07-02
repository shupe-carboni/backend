from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
from app.friedrich.models import (
    FriedrichPricingCustomerResp,
    FriedrichPricingCustomerQuery,
    FriedrichPricingCustomerQueryJSONAPI,
    RelatedFriedrichCustomerResp,
    FriedrichCustomerRelResp,
    RelatedFriedrichPricingResp,
    FriedrichPricingRelResp,
)

from app.jsonapi.sqla_models import FriedrichPricingCustomer

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_PRICING_CUSTOMERS = FriedrichPricingCustomer.__jsonapi_type_override__

friedrich_pricing_customers = APIRouter(
    prefix=f"/{FRIEDRICH_PRICING_CUSTOMERS}", tags=["friedrich", "pricing-customer"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(FriedrichPricingCustomerQueryJSONAPI)


@friedrich_pricing_customers.get(
    "",
    response_model=FriedrichPricingCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_customer_collection(
    token: Token, session: NewSession, query: FriedrichPricingCustomerQuery = Depends()
) -> FriedrichPricingCustomerResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@friedrich_pricing_customers.get(
    "/{friedrich_pricing_customer_id}",
    response_model=FriedrichPricingCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_customer_resource(
    token: Token,
    session: NewSession,
    friedrich_pricing_customer_id: int,
    query: FriedrichPricingCustomerQuery = Depends(),
) -> FriedrichPricingCustomerResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_pricing_customer_id)
    )


@friedrich_pricing_customers.get(
    "/{friedrich_pricing_customer_id}/friedrich-customers",
    response_model=RelatedFriedrichCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_customer_related_friedrich_customers(
    token: Token,
    session: NewSession,
    friedrich_pricing_customer_id: int,
    query: FriedrichPricingCustomerQuery = Depends(),
) -> RelatedFriedrichCustomerResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_pricing_customer_id,
            "friedrich-customers",
        )
    )


@friedrich_pricing_customers.get(
    "/{friedrich_pricing_customer_id}/relationships/friedrich-customers",
    response_model=FriedrichCustomerRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_customer_relationships_friedrich_customers(
    token: Token,
    session: NewSession,
    friedrich_pricing_customer_id: int,
    query: FriedrichPricingCustomerQuery = Depends(),
) -> FriedrichCustomerRelResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_pricing_customer_id,
            "friedrich-customers",
            True,
        )
    )


@friedrich_pricing_customers.get(
    "/{friedrich_pricing_customer_id}/friedrich-pricing",
    response_model=RelatedFriedrichPricingResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_customer_related_friedrich_pricing(
    token: Token,
    session: NewSession,
    friedrich_pricing_customer_id: int,
    query: FriedrichPricingCustomerQuery = Depends(),
) -> RelatedFriedrichPricingResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_pricing_customer_id,
            "friedrich-pricing",
        )
    )


@friedrich_pricing_customers.get(
    "/{friedrich_pricing_customer_id}/relationships/friedrich-pricing",
    response_model=FriedrichPricingRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_customer_relationships_friedrich_pricing(
    token: Token,
    session: NewSession,
    friedrich_pricing_customer_id: int,
    query: FriedrichPricingCustomerQuery = Depends(),
) -> FriedrichPricingRelResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_pricing_customer_id,
            "friedrich-pricing",
            True,
        )
    )


@friedrich_pricing_customers.post("", response_model=None, tags=["jsonapi"])
async def new_friedrich_pricing_customer(token: Token) -> None:
    raise HTTPException(status_code=501)


@friedrich_pricing_customers.patch("", response_model=None, tags=["jsonapi"])
async def mod_friedrich_pricing_customer(token: Token) -> None:
    raise HTTPException(status_code=501)


@friedrich_pricing_customers.delete(
    "/{friedrich_pricing_customer_id}",
    tags=["jsonapi"],
)
async def del_friedrich_pricing_customer(
    token: Token,
    session: NewSession,
    friedrich_pricing_customer_id: int,
    friedrich_customer_id: int,
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichPricingCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(
            session,
            obj_id=friedrich_pricing_customer_id,
            primary_id=friedrich_customer_id,
        )
    )
