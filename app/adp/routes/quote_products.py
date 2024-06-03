from fastapi import HTTPException, Depends, status
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
from app.adp.quotes.products.models import ProductResponse
from app.jsonapi.sqla_models import ADPQuoteProduct

API_TYPE = ADPQuoteProduct.__jsonapi_type_override__
adp_quote_products = APIRouter(
    prefix=f"/{API_TYPE}", tags=["adp quotes", "quote products"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(QuoteQueryJSONAPI)


@adp_quote_products.get("", tags=["jsonapi"])
async def quote_products(token: Token):
    """Intentionally not implemented. Quote products ought to be retreived
    only in the context of the associated quote"""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@adp_quote_products.get("/{product_id}", tags=["jsonapi"])
async def quote_product(token: Token, product_id: int):
    """Intentionally not implemented. Quote products ought to be retreived
    only in the context of the associated quote"""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


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
async def related_quotes(token: Token):
    """Intentionally not implemented. Quote products ought to be retreived
    only in the context of the associated quote"""
    raise HTTPException(status_code=501)


@adp_quote_products.get("/{product_id}/relationships/adp-quotes")
async def product_quotes_relationships(token: Token):
    """Intentionally not implemented. Quote products ought to be retreived
    only in the context of the associated quote"""
    raise HTTPException(status_code=501)
