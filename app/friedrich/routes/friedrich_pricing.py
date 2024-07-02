from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
from app.friedrich.models import (
    FriedrichPricingResp,
    FriedrichPricingQuery,
    FriedrichPricingQueryJSONAPI,
    RelatedFriedrichProductResp,
    FriedrichProductRelResp,
)
from app.jsonapi.sqla_models import FriedrichPricing

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_PRICING = FriedrichPricing.__jsonapi_type_override__

friedrich_pricing = APIRouter(
    prefix=f"/{FRIEDRICH_PRICING}", tags=["friedrich", "pricing-reference"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(FriedrichPricingQueryJSONAPI)


@friedrich_pricing.get(
    "",
    response_model=FriedrichPricingResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_collection(
    token: Token, session: NewSession, query: FriedrichPricingQuery = Depends()
) -> FriedrichPricingResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricing, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@friedrich_pricing.get(
    "/{friedrich_pricing_id}",
    response_model=FriedrichPricingResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_resource(
    token: Token,
    session: NewSession,
    friedrich_pricing_id: int,
    query: FriedrichPricingQuery = Depends(),
) -> FriedrichPricingResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricing, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_pricing_id)
    )


@friedrich_pricing.get(
    "/{friedrich_pricing_id}/friedrich-products",
    response_model=RelatedFriedrichProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_related_friedrich_products(
    token: Token,
    session: NewSession,
    friedrich_pricing_id: int,
    query: FriedrichPricingQuery = Depends(),
) -> RelatedFriedrichProductResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricing, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_pricing_id, "friedrich-products")
    )


@friedrich_pricing.get(
    "/{friedrich_pricing_id}/relationships/friedrich-products",
    response_model=FriedrichProductRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_relationships_friedrich_products(
    token: Token,
    session: NewSession,
    friedrich_pricing_id: int,
    query: FriedrichPricingQuery = Depends(),
) -> FriedrichProductRelResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricing, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session, converter(query), friedrich_pricing_id, "friedrich-products", True
        )
    )


from app.friedrich.models import ModFriedrichPricing


@friedrich_pricing.patch(
    "/{friedrich_pricing_id}",
    response_model=FriedrichPricingResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_friedrich_pricing(
    token: Token,
    session: NewSession,
    friedrich_pricing_id: int,
    mod_data: ModFriedrichPricing,
) -> FriedrichPricingResp:
    return (
        auth.FriedrichOperations(token, FriedrichPricing, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=friedrich_pricing_id,
        )
    )


@friedrich_pricing.delete(
    "/{friedrich_pricing_id}",
    tags=["jsonapi"],
)
async def del_friedrich_pricing(
    token: Token,
    session: NewSession,
    friedrich_pricing_id: int,
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichPricing, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(session, obj_id=friedrich_pricing_id)
    )
