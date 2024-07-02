from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
from app.friedrich.models import (
    FriedrichPricingSpecialResp,
    FriedrichPricingSpecialQuery,
    FriedrichPricingSpecialQueryJSONAPI,
    RelatedFriedrichCustomerResp,
    RelatedFriedrichProductResp,
    FriedrichCustomerRelResp,
    FriedrichProductRelResp,
)
from app.jsonapi.sqla_models import FriedrichPricingSpecial

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_PRICING_SPECIAL = FriedrichPricingSpecial.__jsonapi_type_override__

friedrich_pricing_special = APIRouter(
    prefix=f"/{FRIEDRICH_PRICING_SPECIAL}", tags=["friedrich", "pricing-reference"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(FriedrichPricingSpecialQueryJSONAPI)


@friedrich_pricing_special.get(
    "",
    response_model=FriedrichPricingSpecialResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_collection(
    token: Token, session: NewSession, query: FriedrichPricingSpecialQuery = Depends()
) -> FriedrichPricingSpecialResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecial, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@friedrich_pricing_special.get(
    "/{friedrich_pricing_special_id}",
    response_model=FriedrichPricingSpecialResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_resource(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_id: int,
    query: FriedrichPricingSpecialQuery = Depends(),
) -> FriedrichPricingSpecialResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecial, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_pricing_special_id)
    )


@friedrich_pricing_special.get(
    "/{friedrich_pricing_special_id}/friedrich-customers",
    response_model=RelatedFriedrichCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_related_friedrich_customers(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_id: int,
    query: FriedrichPricingSpecialQuery = Depends(),
) -> RelatedFriedrichCustomerResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecial, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_pricing_special_id,
            "friedrich-customers",
        )
    )


@friedrich_pricing_special.get(
    "/{friedrich_pricing_special_id}/relationships/friedrich-customers",
    response_model=FriedrichCustomerRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_relationships_friedrich_customers(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_id: int,
    query: FriedrichPricingSpecialQuery = Depends(),
) -> FriedrichCustomerRelResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecial, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_pricing_special_id,
            "friedrich-customers",
            True,
        )
    )


@friedrich_pricing_special.get(
    "/{friedrich_pricing_special_id}/friedrich-products",
    response_model=RelatedFriedrichProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_related_friedrich_products(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_id: int,
    query: FriedrichPricingSpecialQuery = Depends(),
) -> RelatedFriedrichProductResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecial, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_pricing_special_id,
            "friedrich-products",
        )
    )


@friedrich_pricing_special.get(
    "/{friedrich_pricing_special_id}/relationships/friedrich-products",
    response_model=FriedrichProductRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_relationships_friedrich_products(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_id: int,
    query: FriedrichPricingSpecialQuery = Depends(),
) -> FriedrichProductRelResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecial, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_pricing_special_id,
            "friedrich-products",
            True,
        )
    )


from app.friedrich.models import ModFriedrichPricingSpecial


@friedrich_pricing_special.patch(
    "/{friedrich_pricing_special_id}",
    response_model=FriedrichPricingSpecialResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_friedrich_pricing_special(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_id: int,
    mod_data: ModFriedrichPricingSpecial,
) -> FriedrichPricingSpecialResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecial, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=friedrich_pricing_special_id,
            primary_id=mod_data.data.relationships.friedrich_customers.data.id,
        )
    )


@friedrich_pricing_special.delete(
    "/{friedrich_pricing_special_id}",
    tags=["jsonapi"],
)
async def del_friedrich_pricing_special(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_id: int,
    friedrich_customer_id: int,
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecial, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session,
            obj_id=friedrich_pricing_special_id,
            primary_id=friedrich_customer_id,
        )
    )
