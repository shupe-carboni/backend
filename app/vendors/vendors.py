from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app import auth
from app.db import SCA_DB
from app.jsonapi.sqla_models import SCAVendor
from app.vendors.models import (
    VendorResponse, VendorInfoResponse, VendorQuery,
    VendorQueryJSONAPI, RelatedVendorResponse,
    VendorRelationshipsResponse, NewVendor, NewVendorInfo,
    VendorModification, VendorInfoModification
)
from app.vendors.utils import add_new_vendor_info, add_new_vendor, modify_existing_vendor, modify_existing_vendor_info

VENDORS_RESOURCE = SCAVendor.__jsonapi_type_override__
vendors = APIRouter(prefix='/vendors', tags=['vendors'])

NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
VendorsPerm = Annotated[auth.VerifiedToken, Depends(auth.vendor_perms_present)]

def convert_query(query: VendorQuery) -> VendorQueryJSONAPI:
    return VendorQueryJSONAPI(**query.model_dump(exclude_none=True)).model_dump(by_alias=True, exclude_none=True)

@vendors.get(
        '',
        response_model=VendorResponse,
        response_model_exclude_none=True
    )
async def vendor_collection(
        token: VendorsPerm,
        session: NewSession,
        query: VendorQuery=Depends()
    ) -> VendorResponse:
    return auth.secured_get_query(
        db=SCA_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['vendors'],
        resource=VENDORS_RESOURCE,
        query=convert_query(query)
    )

@vendors.get(
        '/{vendor_id}',
        response_model=VendorResponse,
        response_model_exclude_none=True
    )
async def vendor(
        token: VendorsPerm,
        session: NewSession,
        vendor_id: int,
        query: VendorQuery=Depends()
    ) -> VendorResponse:
    return auth.secured_get_query(
        db=SCA_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['vendors'],
        resource=VENDORS_RESOURCE,
        query=convert_query(query),
        obj_id=vendor_id
    )

@vendors.get(
        '/{vendor_id}/info',
        response_model=RelatedVendorResponse,
        response_model_exclude_none=True
    )
async def related_info(
        token: VendorsPerm,
        session: NewSession,
        vendor_id: int,
        query: VendorQuery=Depends()
    ) -> None:
    return auth.secured_get_query(
        db=SCA_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['vendors'],
        resource=VENDORS_RESOURCE,
        query=convert_query(query),
        obj_id=vendor_id,
        relationship=False,
        related_resource='info'
    )

@vendors.get(
        '/{vendor_id}/relationships/info',
        response_model=VendorRelationshipsResponse,
        response_model_exclude_none=True
    )
async def info_relationships(
        token: VendorsPerm,
        session: NewSession,
        vendor_id: int,
        query: VendorQuery=Depends()
    ) -> None:
    return auth.secured_get_query(
        db=SCA_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['vendors'],
        resource=VENDORS_RESOURCE,
        query=convert_query(query),
        obj_id=vendor_id,
        relationship=True,
        related_resource='info'
    )

@vendors.post(
        '',
        response_model=VendorResponse,
        response_model_exclude_none=True
    )
async def new_vendor(
        token: VendorsPerm,
        session: NewSession,
        body: NewVendor,
    ) -> VendorResponse:
    if token.permissions.get('vendors') >= auth.VendorPermPriority.sca_employee:
        return add_new_vendor(session=session, payload=body)
    raise HTTPException(status_code=401)

@vendors.patch(
        '/{vendor_id}',
        response_model=VendorResponse,
        response_model_exclude_none=True
    )
async def modify_vendor(
        token: VendorsPerm,
        session: NewSession,
        body: VendorModification,
    ) -> VendorResponse:
    if token.permissions.get('vendors') >= auth.VendorPermPriority.sca_employee:
        return modify_existing_vendor(session, body)
    raise HTTPException(status_code=401)

@vendors.post('/{vendor_id}/info')
async def add_info(
        token: VendorsPerm,
        session: NewSession,
        vendor_id: int,
        body: NewVendorInfo,
    ) -> VendorInfoResponse:
    if token.permissions.get('vendors') >= auth.VendorPermPriority.sca_employee:
        return add_new_vendor_info(session=session, payload=body)
    raise HTTPException(status_code=401)

@vendors.patch('/{vendor_id}/info')
async def modify_info(
        token: VendorsPerm,
        vendor_id: int,
        body: VendorInfoModification,
    ) -> VendorInfoResponse:
    raise HTTPException(status_code=501)

@vendors.delete('/{vendor_id}/info')
async def delete_info(
        token: VendorsPerm,
        vendor_id: int,
    ) -> None:
    raise HTTPException(status_code=501)