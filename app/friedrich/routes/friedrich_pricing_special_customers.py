from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
from app.friedrich.models import (
    FriedrichPricingSpecialCustomerResp,
    FriedrichPricingSpecialCustomerQuery,
    FriedrichPricingSpecialCustomerQueryJSONAPI,
    FriedrichCustomerRelResp,
    RelatedFriedrichCustomerResp,
    FriedrichPricingSpecialRelResp,
    RelatedFriedrichPricingSpecialResp,
)
from app.jsonapi.sqla_models import FriedrichPricingSpecialCustomer

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_PRICING_SPECIAL_CUSTOMERS = (
    FriedrichPricingSpecialCustomer.__jsonapi_type_override__
)

friedrich_pricing_special_customers = APIRouter(
    prefix=f"/{FRIEDRICH_PRICING_SPECIAL_CUSTOMERS}",
    tags=["friedrich", "pricing-customer"],
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(FriedrichPricingSpecialCustomerQueryJSONAPI)


@friedrich_pricing_special_customers.get(
    "",
    response_model=FriedrichPricingSpecialCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_customer_collection(
    token: Token,
    session: NewSession,
    query: FriedrichPricingSpecialCustomerQuery = Depends(),
) -> FriedrichPricingSpecialCustomerResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecialCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@friedrich_pricing_special_customers.get(
    "/{friedrich_pricing_special_customer_id}",
    response_model=FriedrichPricingSpecialCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_customer_resource(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_customer_id: int,
    query: FriedrichPricingSpecialCustomerQuery = Depends(),
) -> FriedrichPricingSpecialCustomerResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecialCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_pricing_special_customer_id)
    )


@friedrich_pricing_special_customers.get(
    "/{friedrich_pricing_special_customer_id}/friedrich-customers",
    response_model=RelatedFriedrichCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_customer_related_friedrich_customers(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_customer_id: int,
    query: FriedrichPricingSpecialCustomerQuery = Depends(),
) -> RelatedFriedrichCustomerResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecialCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_pricing_special_customer_id,
            "friedrich-customers",
        )
    )


@friedrich_pricing_special_customers.get(
    "/{friedrich_pricing_special_customer_id}/relationships/friedrich-customers",
    response_model=FriedrichCustomerRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_customer_relationships_friedrich_customers(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_customer_id: int,
    query: FriedrichPricingSpecialCustomerQuery = Depends(),
) -> FriedrichCustomerRelResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecialCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_pricing_special_customer_id,
            "friedrich-customers",
            True,
        )
    )


@friedrich_pricing_special_customers.get(
    "/{friedrich_pricing_special_customer_id}/friedrich-pricing-special",
    response_model=RelatedFriedrichPricingSpecialResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_customer_related_friedrich_pricing_special(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_customer_id: int,
    query: FriedrichPricingSpecialCustomerQuery = Depends(),
) -> RelatedFriedrichPricingSpecialResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecialCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_pricing_special_customer_id,
            "friedrich-pricing-special",
        )
    )


@friedrich_pricing_special_customers.get(
    "/{friedrich_pricing_special_customer_id}/relationships/friedrich-pricing-special",
    response_model=FriedrichPricingSpecialRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_customer_relationships_friedrich_pricing_special(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_customer_id: int,
    query: FriedrichPricingSpecialCustomerQuery = Depends(),
) -> FriedrichPricingSpecialRelResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecialCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_pricing_special_customer_id,
            "friedrich-pricing-special",
            True,
        )
    )


@friedrich_pricing_special_customers.delete(
    "/{friedrich_pricing_special_customer_id}",
    tags=["jsonapi"],
)
async def del_friedrich_pricing_special_customer(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_customer_id: int,
    friedrich_customer_id: int,
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecialCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(
            session,
            obj_id=friedrich_pricing_special_customer_id,
            primary_id=friedrich_customer_id,
        )
    )
