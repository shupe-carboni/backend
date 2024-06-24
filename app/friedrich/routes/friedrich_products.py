
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.friedrich.models import (
    FriedrichProductResp,
    FriedrichProductQuery,
    FriedrichProductQueryJSONAPI,
)
from app.jsonapi.sqla_models import FriedrichProduct

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_PRODUCTS = FriedrichProduct.__jsonapi_type_override__

friedrich_products = APIRouter(
    prefix=f"/{FRIEDRICH_PRODUCTS}", tags=["friedrich", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(FriedrichProductQueryJSONAPI)


@friedrich_products.get(
    "",
    response_model=FriedrichProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_product_collection(
    token: Token, session: NewSession, query: FriedrichProductQuery = Depends()
) -> FriedrichProductResp:
    return (
        auth.FriedrichOperations(token, FriedrichProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@friedrich_products.get(
    "/{friedrich_product_id}",
    response_model=FriedrichProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_product_resource(
    token: Token,
    session: NewSession,
    friedrich_product_id: int,
    query: FriedrichProductQuery = Depends(),
) -> FriedrichProductResp:
    return (
        auth.FriedrichOperations(token, FriedrichProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_product_id)
    )


@friedrich_products.get(
    "/{friedrich_product_id}/RELATED_RESOURCE",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_product_related_RELATED_RESOURCE(
    token: Token,
    session: NewSession,
    friedrich_product_id: int,
    query: FriedrichProductQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_product_id, "RELATED_RESOURCE")
    )


@friedrich_products.get(
    "/{friedrich_product_id}/relationships/RELATED_RESOURCE",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_product_relationships_RELATED_RESOURCE(
    token: Token,
    session: NewSession,
    friedrich_product_id: int,
    query: FriedrichProductQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_product_id, "RELATED_RESOURCE", True)
    )

    