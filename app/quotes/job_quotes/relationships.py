from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth

from app.vendors.models import RelatedVendorResponse, VendorRelationshipsResponse
from app.customers.models import RelatedCustomerResponse, CustomerRelationshipsResponse
from app.places.models import RelatedPlaceResponse, PlaceRelationshipsResponse
from app.quotes.products.models import RelatedProductResponse, ProductRelationshipsResponse

quote_rel = APIRouter(tags=['quotes'])

@quote_rel.get('/{quote_id}/vendors')
async def related_vendor(
        quote_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> RelatedVendorResponse:
    raise HTTPException(status_code=501)

@quote_rel.get('/{quote_id}/places')
async def related_place(
        quote_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> RelatedPlaceResponse:
    raise HTTPException(status_code=501)

@quote_rel.get('/{quote_id}/customers')
async def related_customer(
        quote_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> RelatedCustomerResponse:
    raise HTTPException(status_code=501)

@quote_rel.get('/{quote_id}/products')
async def related_products(
        quote_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> RelatedProductResponse:
    raise HTTPException(status_code=501)

@quote_rel.get('/{quote_id}/relationships/vendors')
async def quote_vendor_relationships(
        quote_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> VendorRelationshipsResponse:
    raise HTTPException(status_code=501)

@quote_rel.get('/{quote_id}/relationships/places')
async def quote_place_relationships(
        quote_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> PlaceRelationshipsResponse:
    raise HTTPException(status_code=501)

@quote_rel.get('/{quote_id}/relationships/customers')
async def quote_customer_relationships(
        quote_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> CustomerRelationshipsResponse:
    raise HTTPException(status_code=501)

@quote_rel.get('/{quote_id}/relationships/products')
async def quote_products_relationships(
        quote_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> ProductRelationshipsResponse:
    raise HTTPException(status_code=501)
