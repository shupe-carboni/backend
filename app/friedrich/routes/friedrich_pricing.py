
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.friedrich.models import (
    FriedrichPricingResp,
    FriedrichPricingQuery,
    FriedrichPricingQueryJSONAPI,
)
from app.jsonapi.sqla_models import FriedrichPricing

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_PRICING = FriedrichPricing.__jsonapi_type_override__

friedrich_pricing = APIRouter(
    prefix=f"/{FRIEDRICH_PRICING}", tags=["friedrich", ""]
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
    token: Token, session: NewSession, query: FriedrichPricingQuery
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
    query: FriedrichPricingQuery,
    friedrich_pricing_id: int,
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
    "/{friedrich_pricing_id}/RELATED_RESOURCE",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_related_RELATED_RESOURCE(
    token: Token,
    session: NewSession,
    query: FriedrichPricingQuery,
    friedrich_pricing_id: int,
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichPricing, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_pricing_id, "RELATED_RESOURCE")
    )


@friedrich_pricing.get(
    "/{friedrich_pricing_id}/relationships/RELATED_RESOURCE",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_relationships_RELATED_RESOURCE(
    token: Token,
    session: NewSession,
    query: FriedrichPricingQuery,
    friedrich_pricing_id: int,
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichPricing, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_pricing_id, "RELATED_RESOURCE", True)
    )

    