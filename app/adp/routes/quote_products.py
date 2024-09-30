from fastapi import HTTPException, Depends, status
from fastapi.routing import APIRouter
from typing import Annotated
from app import auth
from app.db import ADP_DB
from sqlalchemy.orm import Session
from app.jsonapi.core_models import convert_query
from app.adp.quotes.products.models import (
    ProductResponse,
    NewProductRequest,
    ExistingProductRequest,
    QuoteProductQueryJSONAPI,
)
from app.jsonapi.sqla_models import ADPQuoteProduct
from logging import getLogger

logger = getLogger("uvicorn.info")

PARENT_PREFIX = "/vendors/adp"
API_TYPE = ADPQuoteProduct.__jsonapi_type_override__
adp_quote_products = APIRouter(
    prefix=f"/{API_TYPE}", tags=["adp quotes", "quote products"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(QuoteProductQueryJSONAPI)


@adp_quote_products.get("", tags=["jsonapi"])
async def quote_products(token: Token):
    """Intentionally not implemented. Quote products ought to be retreived
    only in the context of the associated quote"""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, quote_products.__doc__)


@adp_quote_products.get("/{product_id}", tags=["jsonapi"])
async def quote_product(token: Token, product_id: int):
    """Intentionally not implemented. Quote products ought to be retreived
    only in the context of the associated quote"""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, quote_product.__doc__)


@adp_quote_products.post(
    "",
    response_model=ProductResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_quote_product(
    token: Token, session: NewSession, new_quote_product: NewProductRequest
) -> ProductResponse:
    if token.permissions < auth.Permissions.developer:
        price = new_quote_product.data.attributes.price
        model_number = new_quote_product.data.attributes.model_number
        forbidden_to_add = (price, model_number)
        if any(forbidden_to_add):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "adding a new quote product with a quoted model number and/or a price "
                "is reserved for SCA only",
            )
    return (
        auth.ADPQuoteOperations(token, ADPQuoteProduct, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_customer("std")
        .post(
            session=session,
            data=new_quote_product.model_dump(exclude_none=True, by_alias=True),
            primary_id=new_quote_product.data.relationships.adp_quotes.data.id,
        )
    )


@adp_quote_products.patch(
    "/{product_id}",
    response_model=ExistingProductRequest,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_quote_product(
    token: Token,
    session: NewSession,
    mod_quote_prod: ExistingProductRequest,
    product_id: int,
) -> ProductResponse:
    data = mod_quote_prod.model_dump(exclude_none=True, by_alias=True)
    attributes = mod_quote_prod.data.attributes
    if token.permissions < auth.Permissions.developer:
        forbidden_to_change = (
            attributes.price,
            attributes.model_number,
        )
        if any(forbidden_to_change):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "modifying a quote product's quoted model number and/or a price "
                "is reserved for SCA only",
            )
    if attributes.comp_model:
        data["data"]["attributes"]["model-number"] = None
        data["data"]["attributes"]["price"] = None
        logger.warning(
            "Model Number and Price have been nulled due to the presence of "
            "a comp-model in the PATCH request"
        )
    return (
        auth.ADPQuoteOperations(token, ADPQuoteProduct, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_customer("std")
        .patch(
            session=session,
            data=data,
            primary_id=mod_quote_prod.data.relationships.adp_quotes.data.id,
            obj_id=product_id,
        )
    )


@adp_quote_products.delete("/{product_id}")
async def delete_quote_product(
    token: Token, session: NewSession, product_id: int, quote_id: int
) -> None:
    return (
        auth.ADPQuoteOperations(token, ADPQuoteProduct, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_customer("std")
        .delete(session=session, obj_id=product_id, primary_id=quote_id)
    )


@adp_quote_products.get("/{product_id}/adp-quotes")
async def related_quotes(token: Token):
    """Intentionally not implemented. Quote products ought to be retreived
    only in the context of the associated quote"""
    raise HTTPException(status_code=501)


@adp_quote_products.get("/{product_id}/relationships/adp-quotes")
async def product_quotes_relationships(token: Token):
    """Intentionally not implemented. Quote products ought to be retreived
    only in the context of the associated quote"""
    raise HTTPException(status_code=501)
