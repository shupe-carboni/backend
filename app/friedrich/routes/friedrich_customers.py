from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
from app.customers.models import RelatedCustomerResponse, CustomerRelationshipsResponse
from app.friedrich.models import (
    FriedrichCustomerResp,
    FriedrichCustomerQuery,
    FriedrichCustomerQueryJSONAPI,
    RelatedFriedrichPricingSpecialResp,
    RelatedFriedrichCustomerPriceLevelResp,
    FriedrichPricingSpecialRelResp,
    FriedrichCustomerPriceLevelRelResp,
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
    token: Token, session: NewSession, query: FriedrichCustomerQuery = Depends()
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
    friedrich_customer_id: int,
    query: FriedrichCustomerQuery = Depends(),
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
    "/{friedrich_customer_id}/customers",
    response_model=RelatedCustomerResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_related_customers(
    token: Token,
    session: NewSession,
    friedrich_customer_id: int,
    query: FriedrichCustomerQuery = Depends(),
) -> RelatedCustomerResponse:
    return (
        auth.FriedrichOperations(token, FriedrichCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_customer_id, "customers")
    )


@friedrich_customers.get(
    "/{friedrich_customer_id}/relationships/customers",
    response_model=CustomerRelationshipsResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_relationships_customers(
    token: Token,
    session: NewSession,
    friedrich_customer_id: int,
    query: FriedrichCustomerQuery = Depends(),
) -> CustomerRelationshipsResponse:
    return (
        auth.FriedrichOperations(token, FriedrichCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_customer_id, "customers", True)
    )


@friedrich_customers.get(
    "/{friedrich_customer_id}/friedrich-pricing-special",
    response_model=RelatedFriedrichPricingSpecialResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_related_friedrich_pricing_special(
    token: Token,
    session: NewSession,
    friedrich_customer_id: int,
    query: FriedrichCustomerQuery = Depends(),
) -> RelatedFriedrichPricingSpecialResp:
    return (
        auth.FriedrichOperations(token, FriedrichCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_customer_id,
            "friedrich-pricing-special",
        )
    )


@friedrich_customers.get(
    "/{friedrich_customer_id}/relationships/friedrich-pricing-special",
    response_model=FriedrichPricingSpecialRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_relationships_friedrich_pricing_special(
    token: Token,
    session: NewSession,
    friedrich_customer_id: int,
    query: FriedrichCustomerQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_customer_id,
            "friedrich-pricing-special",
            True,
        )
    )


@friedrich_customers.get(
    "/{friedrich_customer_id}/friedrich-customer-price-levels",
    response_model=RelatedFriedrichCustomerPriceLevelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_related_friedrich_customer_price_levels(
    token: Token,
    session: NewSession,
    friedrich_customer_id: int,
    query: FriedrichCustomerQuery = Depends(),
) -> RelatedFriedrichCustomerPriceLevelResp:
    return (
        auth.FriedrichOperations(token, FriedrichCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_customer_id,
            "friedrich-customer-price-levels",
        )
    )


@friedrich_customers.get(
    "/{friedrich_customer_id}/relationships/friedrich-customer-price-levels",
    response_model=FriedrichCustomerPriceLevelRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_customer_relationships_friedrich_customer_price_levels(
    token: Token,
    session: NewSession,
    friedrich_customer_id: int,
    query: FriedrichCustomerQuery = Depends(),
) -> FriedrichCustomerPriceLevelRelResp:
    return (
        auth.FriedrichOperations(token, FriedrichCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_customer_id,
            "friedrich-customer-price-levels",
            True,
        )
    )


from app.friedrich.models import ModFriedrichCustomer


@friedrich_customers.patch(
    "/{friedrich_customer_id}",
    response_model=FriedrichCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_friedrich_customer(
    token: Token,
    session: NewSession,
    friedrich_customer_id: int,
    mod_data: ModFriedrichCustomer,
) -> FriedrichCustomerResp:
    return (
        auth.FriedrichOperations(token, FriedrichCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=friedrich_customer_id,
        )
    )


@friedrich_customers.delete(
    "/{friedrich_customer_id}",
    tags=["jsonapi"],
)
async def del_friedrich_customer(
    token: Token,
    session: NewSession,
    friedrich_customer_id: int,
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(session, obj_id=friedrich_customer_id)
    )
