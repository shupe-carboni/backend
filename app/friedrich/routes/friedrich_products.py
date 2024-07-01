from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
from app.friedrich.models import (
    FriedrichProductResp,
    FriedrichProductQuery,
    FriedrichProductQueryJSONAPI,
    RelatedFriedrichPricingResp,
    RelatedFriedrichPricingSpecialResp,
    FriedrichPricingRelResp,
    FriedrichPricingSpecialRelResp,
)
from app.jsonapi.sqla_models import FriedrichProduct

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_PRODUCTS = FriedrichProduct.__jsonapi_type_override__

friedrich_products = APIRouter(
    prefix=f"/{FRIEDRICH_PRODUCTS}", tags=["friedrich", "products"]
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
    "/{friedrich_product_id}/friedrich-pricing",
    response_model=RelatedFriedrichPricingResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_product_related_friedrich_pricing(
    token: Token,
    session: NewSession,
    friedrich_product_id: int,
    query: FriedrichProductQuery = Depends(),
) -> RelatedFriedrichPricingResp:
    return (
        auth.FriedrichOperations(token, FriedrichProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_product_id, "friedrich-pricing")
    )


@friedrich_products.get(
    "/{friedrich_product_id}/relationships/friedrich-pricing",
    response_model=FriedrichPricingRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_product_relationships_friedrich_pricing(
    token: Token,
    session: NewSession,
    friedrich_product_id: int,
    query: FriedrichProductQuery = Depends(),
) -> FriedrichPricingRelResp:
    return (
        auth.FriedrichOperations(token, FriedrichProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_product_id, "friedrich-pricing", True)
    )


@friedrich_products.get(
    "/{friedrich_product_id}/friedrich-pricing-special",
    response_model=RelatedFriedrichPricingSpecialResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_product_related_friedrich_pricing_special(
    token: Token,
    session: NewSession,
    friedrich_product_id: int,
    query: FriedrichProductQuery = Depends(),
) -> RelatedFriedrichPricingSpecialResp:
    return (
        auth.FriedrichOperations(token, FriedrichProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session, converter(query), friedrich_product_id, "friedrich-pricing-special"
        )
    )


@friedrich_products.get(
    "/{friedrich_product_id}/relationships/friedrich-pricing-special",
    response_model=FriedrichPricingSpecialRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_product_relationships_friedrich_pricing_special(
    token: Token,
    session: NewSession,
    friedrich_product_id: int,
    query: FriedrichProductQuery = Depends(),
) -> FriedrichPricingSpecialRelResp:
    return (
        auth.FriedrichOperations(token, FriedrichProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_product_id,
            "friedrich-pricing-special",
            True,
        )
    )


from app.friedrich.models import ModFriedrichProduct


@friedrich_products.patch(
    "/{friedrich_product_id}",
    response_model=FriedrichProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_friedrich_product(
    token: Token,
    session: NewSession,
    friedrich_product_id: int,
    mod_data: ModFriedrichProduct,
) -> FriedrichProductResp:
    return (
        auth.FriedrichOperations(token, FriedrichProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=friedrich_product_id,
        )
    )


@friedrich_products.delete(
    "/{friedrich_product_id}",
    tags=["jsonapi"],
)
async def del_friedrich_product(
    token: Token,
    session: NewSession,
    friedrich_product_id: int,
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(session, obj_id=friedrich_product_id)
    )
