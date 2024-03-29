from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import ADP_DB

from app.customers.models import RelatedCustomerResponse, CustomerRelationshipsResponse
from app.places.models import RelatedPlaceResponse, PlaceRelationshipsResponse
from app.adp.quotes.products.models import RelatedProductResponse, ProductRelationshipsResponse

quote_rel = APIRouter(tags=['quotes'])

ADPQuotesPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_quotes_perms)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]

@quote_rel.get('/{quote_id}/place')
async def related_place(
        token: ADPQuotesPerm,
        session: NewSession,
        quote_id: int,
    ) -> RelatedPlaceResponse:
    raise HTTPException(status_code=501)

@quote_rel.get('/{quote_id}/customer')
async def related_customer(
        token: ADPQuotesPerm,
        session: NewSession,
        quote_id: int,
    ) -> RelatedCustomerResponse:
    raise HTTPException(status_code=501)

@quote_rel.get('/{quote_id}/products')
async def related_products(
        quote_id: int,
        token: ADPQuotesPerm,
        session: NewSession,
    ) -> RelatedProductResponse:
    raise HTTPException(status_code=501)

@quote_rel.get('/{quote_id}/relationships/place')
async def quote_place_relationships(
        token: ADPQuotesPerm,
        session: NewSession,
        quote_id: int,
    ) -> PlaceRelationshipsResponse:
    raise HTTPException(status_code=501)

@quote_rel.get('/{quote_id}/relationships/customer')
async def quote_customer_relationships(
        quote_id: int,
        token: ADPQuotesPerm,
        session: NewSession,
    ) -> CustomerRelationshipsResponse:
    raise HTTPException(status_code=501)

@quote_rel.get('/{quote_id}/relationships/products')
async def quote_products_relationships(
        token: ADPQuotesPerm,
        session: NewSession,
        quote_id: int,
    ) -> ProductRelationshipsResponse:
    raise HTTPException(status_code=501)
