from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from typing import Annotated
from app import auth
from app.db import ADP_DB
from sqlalchemy.orm import Session
from app.jsonapi.core_models import convert_query
from app.adp.quotes.job_quotes.models import (
    RelatedQuoteResponse,
    QuoteRelationshipsResponse,
    QuoteQueryJSONAPI,
)
from app.adp.quotes.products.models import ProductResponse, QuoteProductQuery
from app.jsonapi.sqla_models import ADPQuoteProduct

API_TYPE = ADPQuoteProduct.__jsonapi_type_override__
adp_quote_products = APIRouter(
    prefix=f"/{API_TYPE}", tags=["adp quotes", "quote products"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(QuoteQueryJSONAPI)


@adp_quote_products.get(
    "",
    response_model=ProductResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def quote_products(
    token: Token, session: NewSession, query: QuoteProductQuery = Depends()
) -> ProductResponse:
    return (
        auth.ADPOperations(token, API_TYPE)
        .allow_admin()
        .allow_dev()
        .allow_sca()
        .allow_customer("std")
        .get(session=session, query=converter(query))
    )


@adp_quote_products.get(
    "/{product_id}",
    response_model=ProductResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def quote_product(
    token: Token,
    session: NewSession,
    product_id: int,
    query: QuoteProductQuery = Depends(),
) -> ProductResponse:
    return (
        auth.ADPOperations(token, API_TYPE)
        .allow_admin()
        .allow_dev()
        .allow_sca()
        .allow_customer("std")
        .get(session=session, query=converter(query), obj_id=product_id)
    )


@adp_quote_products.post(
    "",
    response_model=ProductResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_quote_product(
    token: Token,
    session: NewSession,
) -> ProductResponse:
    raise HTTPException(status_code=501)


@adp_quote_products.patch("/{product_id}")
async def mod_quote_product(
    token: Token,
    session: NewSession,
) -> ProductResponse:
    raise HTTPException(status_code=501)


@adp_quote_products.delete("/{product_id}")
async def delete_quote_product(
    token: Token,
    session: NewSession,
) -> None:
    raise HTTPException(status_code=501)


@adp_quote_products.get("/{product_id}/adp-quotes")
async def related_quotes(
    token: Token,
    session: NewSession,
) -> RelatedQuoteResponse:
    raise HTTPException(status_code=501)


@adp_quote_products.get("/{product_id}/relationships/adp-quotes")
async def product_quotes_relationships(
    token: Token,
    session: NewSession,
) -> QuoteRelationshipsResponse:
    raise HTTPException(status_code=501)
