
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth
from app.vendors.models import (
    VendorResponse,
    VendorInfoResponse,
    VendorQuery,
    NewVendorInfoResourceObject,
    ExistingVendorInfo
)

vendors = APIRouter(prefix='/vendors', tags=['vendors'])


@vendors.get('', response_model=VendorResponse)
async def vendor_collection(
        query: VendorQuery=Depends(), # type: ignore
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> VendorResponse:
    raise HTTPException(status_code=501)

@vendors.get('/{vendor_id}')
async def vendor(
        vendor_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> VendorResponse:
    raise HTTPException(status_code=501)

@vendors.post('/{vendor_id}/info')
async def add_info(
        body: NewVendorInfoResourceObject,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> VendorInfoResponse:
    raise HTTPException(status_code=501)

@vendors.patch('/{vendor_id}/info')
async def modify_info(
        vendor_id: int,
        body: ExistingVendorInfo,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> VendorInfoResponse:
    raise HTTPException(status_code=501)

@vendors.delete('/{vendor_id}/info')
async def delete_info(
        vendor_id: int,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> None:
    raise HTTPException(status_code=501)