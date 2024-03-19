from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth
from app.vendors.models import (
    VendorResponse,
    VendorInfoResponse,
    VendorQuery,
    NewVendorInfoResourceObject,
    ExistingVendorInfo,
    VendorQueryJSONAPI
)

vendors = APIRouter(prefix='/vendors', tags=['vendors'])

VendorsPerm = Annotated[auth.VerifiedToken, Depends(auth.vendor_perms_present)]

def convert_query(query: VendorQuery) -> VendorQueryJSONAPI:
    return VendorQueryJSONAPI(**query.model_dump(exclude_none=True)).model_dump(by_alias=True, exclude_none=True)

@vendors.get('', response_model=VendorResponse)
async def vendor_collection(
        token: VendorsPerm,
        query: VendorQuery=Depends()
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