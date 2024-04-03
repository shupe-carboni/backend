
from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app import auth
from app.db import SCA_DB
from app.jsonapi.sqla_models import SCAVendorInfo, SCAVendor
from app.jsonapi.core_models import convert_query
from app.vendors.models import (
    VendorInfoResponse, NewVendorInfo,
    VendorInfoModification, VendorInfoQuery,
    VendorInfoQueryJSONAPI
)
from app.vendors.utils import add_new_vendor_info, modify_existing_vendor_info, delete_vendor_info

INFO_RESOURCE = SCAVendorInfo.__jsonapi_type_override__
VENDOR_RESOURCE = SCAVendor.__jsonapi_type_override__
vendors_info = APIRouter(prefix=f'/{INFO_RESOURCE}', tags=['vendor info'])

NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
VendorsPerm = Annotated[auth.VerifiedToken, Depends(auth.vendor_perms_present)]
converter = convert_query(VendorInfoQueryJSONAPI)

@vendors_info.get('')
async def info(
        token: VendorsPerm,
        session: NewSession,
        query: VendorInfoQuery
    ) -> VendorInfoResponse:
    if token.permissions.get('vendors') >= auth.VendorPermPriority.view_only:
        return auth.secured_get_query(
            db=SCA_DB,
            session=session,
            token=token,
            auth_scheme=auth.Permissions['vendors'],
            resource=INFO_RESOURCE,
            query=converter(query)
        )
    raise HTTPException(status_code=401)

@vendors_info.get('/{info_id}')
async def info(
        token: VendorsPerm,
        session: NewSession,
        info_id: int,
        query: VendorInfoQuery
    ) -> VendorInfoResponse:
    if token.permissions.get('vendors') >= auth.VendorPermPriority.view_only:
        return auth.secured_get_query(
            db=SCA_DB,
            session=session,
            token=token,
            auth_scheme=auth.Permissions['vendors'],
            resource=INFO_RESOURCE,
            query=converter(query),
            obj_id=info_id
        )
    raise HTTPException(status_code=401)

@vendors_info.get('/{info_id}/vendors')
async def info_related_vendor(
        token: VendorsPerm,
        session: NewSession,
        info_id: int,
        query: VendorInfoQuery
    ) -> VendorInfoResponse:
    if token.permissions.get('vendors') >= auth.VendorPermPriority.view_only:
        return auth.secured_get_query(
            db=SCA_DB,
            session=session,
            token=token,
            auth_scheme=auth.Permissions['vendors'],
            resource=INFO_RESOURCE,
            query=converter(query),
            obj_id=info_id,
            related_resource=VENDOR_RESOURCE
        )
    raise HTTPException(status_code=401)

@vendors_info.get('/{info_id}/relationships/vendors')
async def info_vendors_relationships(
        token: VendorsPerm,
        session: NewSession,
        info_id: int,
        query: VendorInfoQuery
    ) -> VendorInfoResponse:
    if token.permissions.get('vendors') >= auth.VendorPermPriority.view_only:
        return auth.secured_get_query(
            db=SCA_DB,
            session=session,
            token=token,
            auth_scheme=auth.Permissions['vendors'],
            resource=INFO_RESOURCE,
            query=converter(query),
            obj_id=info_id,
            relationship=True,
            related_resource=VENDOR_RESOURCE
        )
    raise HTTPException(status_code=401)

@vendors_info.post('')
async def add_info(
        token: VendorsPerm,
        session: NewSession,
        body: NewVendorInfo,
    ) -> VendorInfoResponse:
    if token.permissions.get('vendors') >= auth.VendorPermPriority.sca_employee:
        return add_new_vendor_info(session=session, payload=body)
    raise HTTPException(status_code=401)

@vendors_info.patch('/{info_id}')
async def modify_info(
        token: VendorsPerm,
        session: NewSession,
        info_id: int,
        body: VendorInfoModification,
    ) -> VendorInfoResponse:
    if token.permissions.get('vendors') >= auth.VendorPermPriority.sca_employee:
        return modify_existing_vendor_info(session=session, payload=body, obj_id=info_id)
    raise HTTPException(status_code=401)

@vendors_info.delete('/{info_id}')
async def delete_info(
        token: VendorsPerm,
        session: NewSession,
        info_id: int,
    ) -> None:
    if token.permissions.get('vendors') >= auth.VendorPermPriority.sca_employee:
        return delete_vendor_info(session=session, obj_id=info_id)
    raise HTTPException(status_code=401)