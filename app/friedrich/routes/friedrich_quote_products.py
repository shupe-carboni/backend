
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.friedrich.models import (
    FriedrichQuoteProductResp,
    FriedrichQuoteProductQuery,
    FriedrichQuoteProductQueryJSONAPI,
)
from app.jsonapi.sqla_models import FriedrichQuoteProduct

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_QUOTE_PRODUCTS = FriedrichQuoteProduct.__jsonapi_type_override__

friedrich_quote_products = APIRouter(
    prefix=f"/{FRIEDRICH_QUOTE_PRODUCTS}", tags=["friedrich", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(FriedrichQuoteProductQueryJSONAPI)


@friedrich_quote_products.get(
    "",
    response_model=FriedrichQuoteProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_product_collection(
    token: Token, session: NewSession, query: FriedrichQuoteProductQuery = Depends()
) -> FriedrichQuoteProductResp:
    return (
        auth.FriedrichOperations(token, FriedrichQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@friedrich_quote_products.get(
    "/{friedrich_quote_product_id}",
    response_model=FriedrichQuoteProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_product_resource(
    token: Token,
    session: NewSession,
    friedrich_quote_product_id: int,
    query: FriedrichQuoteProductQuery = Depends(),
) -> FriedrichQuoteProductResp:
    return (
        auth.FriedrichOperations(token, FriedrichQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_quote_product_id)
    )


@friedrich_quote_products.get(
    "/{friedrich_quote_product_id}/friedrich-quotes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_product_related_friedrich_quotes(
    token: Token,
    session: NewSession,
    friedrich_quote_product_id: int,
    query: FriedrichQuoteProductQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_quote_product_id, "friedrich-quotes")
    )

@friedrich_quote_products.get(
    "/{friedrich_quote_product_id}/relationships/friedrich-quotes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_product_relationships_friedrich_quotes(
    token: Token,
    session: NewSession,
    friedrich_quote_product_id: int,
    query: FriedrichQuoteProductQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_quote_product_id, "friedrich-quotes", True)
    )

    
@friedrich_quote_products.get(
    "/{friedrich_quote_product_id}/friedrich-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_product_related_friedrich_products(
    token: Token,
    session: NewSession,
    friedrich_quote_product_id: int,
    query: FriedrichQuoteProductQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_quote_product_id, "friedrich-products")
    )

@friedrich_quote_products.get(
    "/{friedrich_quote_product_id}/relationships/friedrich-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_product_relationships_friedrich_products(
    token: Token,
    session: NewSession,
    friedrich_quote_product_id: int,
    query: FriedrichQuoteProductQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_quote_product_id, "friedrich-products", True)
    )

    

from app.friedrich.models import ModFriedrichQuoteProduct

@friedrich_quote_products.patch(
    "/{friedrich_quote_product_id}",
    response_model=FriedrichQuoteProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_friedrich_quote_product(
    token: Token,
    session: NewSession,
    friedrich_quote_product_id: int,
    mod_data: ModFriedrichQuoteProduct,
) -> FriedrichQuoteProductResp:
    return (
        auth.FriedrichOperations(token, FriedrichQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=friedrich_quote_product_id,
                primary_id=mod_data.data.relationships.friedrich_customers.data.id
            )
        )

        
@friedrich_quote_products.delete(
    "/{friedrich_quote_product_id}",
    tags=["jsonapi"],
)
async def del_friedrich_quote_product(
    token: Token,
    session: NewSession,
    friedrich_quote_product_id: int,
    friedrich_customer_id: int,
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=friedrich_quote_product_id, primary_id=friedrich_customer_id)
    )
    