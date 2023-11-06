
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth
from app.vendors.models import (
    VendorResponse,
    VendorDetailResponse,
    VendorQuery,
    NewVendorResourceObject,
    NewVendorDetailResourceObject,
    ExistingVendor,
    ExistingVendorDetail
)

vendors = APIRouter(prefix='/vendors', tags=['vendors'])


@vendors.get('', response_model=VendorResponse)
async def vendors_collection(
        query: VendorQuery=Depends(),
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> VendorResponse:
    raise HTTPException(status_code=501)

@vendors.get('/{vendor_id}')
async def vendor_detail(
        vendor_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> VendorResponse:
    raise HTTPException(status_code=501)

@vendors.delete('/{vendor_id}')
async def delete_vendor(
        vendor_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)) -> None:
    raise HTTPException(status_code=501)

@vendors.post('')
async def new_vendor(
        body: NewVendorResourceObject,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)) -> VendorResponse:
    raise HTTPException(status_code=501)

@vendors.post('/{vendor_id}/products')
async def add_products(
        body: NewVendorDetailResourceObject,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)) -> VendorDetailResponse:
    raise HTTPException(status_code=501)

@vendors.patch('/{vendor_id}')
async def modify_vendor(
        vendor_id: int,
        body: ExistingVendor,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)) -> VendorResponse:
    raise HTTPException(status_code=501)

@vendors.patch('/{vendor_id}/products')
async def modify_products(
        vendor_id: int,
        body: ExistingVendorDetail,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)) -> VendorDetailResponse:
    raise HTTPException(status_code=501)