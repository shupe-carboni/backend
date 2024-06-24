
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.friedrich.models import (
    FriedrichPricingSpecialResp,
    FriedrichPricingSpecialQuery,
    FriedrichPricingSpecialQueryJSONAPI,
)
from app.jsonapi.sqla_models import FriedrichPricingSpecial

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_PRICING_SPECIAL = FriedrichPricingSpecial.__jsonapi_type_override__

friedrich_pricing_special = APIRouter(
    prefix=f"/{FRIEDRICH_PRICING_SPECIAL}", tags=["friedrich", ""]
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
    "/{friedrich_pricing_special_id}/RELATED_RESOURCE",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_related_RELATED_RESOURCE(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_id: int,
    query: FriedrichPricingSpecialQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecial, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_pricing_special_id, "RELATED_RESOURCE")
    )


@friedrich_pricing_special.get(
    "/{friedrich_pricing_special_id}/relationships/RELATED_RESOURCE",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_pricing_special_relationships_RELATED_RESOURCE(
    token: Token,
    session: NewSession,
    friedrich_pricing_special_id: int,
    query: FriedrichPricingSpecialQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichPricingSpecial, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_pricing_special_id, "RELATED_RESOURCE", True)
    )

    