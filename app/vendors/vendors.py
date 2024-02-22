from typing import Annotated
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

VendorsPerm = Annotated[auth.VerifiedToken, Depends(auth.vendor_perms_present)]

@vendors.get('', response_model=VendorResponse)
async def vendor_collection(
        token: VendorsPerm,
        query: VendorQuery=Depends(), # type: ignore
    ) -> VendorResponse:
    raise HTTPException(status_code=501)

@vendors.get('/{vendor_id}')
async def vendor(
        token: VendorsPerm,
        vendor_id: int,
    ) -> VendorResponse:
    raise HTTPException(status_code=501)

@vendors.post('/{vendor_id}/info')
async def add_info(
        token: VendorsPerm,
        body: NewVendorInfoResourceObject,
    ) -> VendorInfoResponse:
    raise HTTPException(status_code=501)

@vendors.patch('/{vendor_id}/info')
async def modify_info(
        token: VendorsPerm,
        vendor_id: int,
        body: ExistingVendorInfo,
    ) -> VendorInfoResponse:
    raise HTTPException(status_code=501)

@vendors.delete('/{vendor_id}/info')
async def delete_info(
        token: VendorsPerm,
        vendor_id: int,
    ) -> None:
    raise HTTPException(status_code=501)