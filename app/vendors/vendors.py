from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app import auth
from app.db import SCA_DB
from app.jsonapi.sqla_models import SCAVendor
from app.jsonapi.core_models import convert_query
from app.vendors.models import (
    VendorResponse, VendorQuery,
    VendorQueryJSONAPI, RelatedVendorInfoResponse,
    VendorRelationshipsResponse, NewVendor,
    VendorModification
)
from app.vendors.utils import (
    add_new_vendor, modify_existing_vendor,
    delete_vendor, delete_vendor_info
)

VENDORS_RESOURCE = SCAVendor.__jsonapi_type_override__
vendors = APIRouter(prefix=f'/{VENDORS_RESOURCE}', tags=['vendors'])

NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
VendorsPerm = Annotated[auth.VerifiedToken, Depends(auth.vendor_perms_present)]
converter = convert_query(VendorQueryJSONAPI)

@vendors.get(
        '',
        tags=['jsonapi'],
        response_model=VendorResponse,
        response_model_exclude_none=True)
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
        query=converter(query))

@vendors.get(
        '/{vendor_id}',
        tags=['jsonapi'],
        response_model=VendorResponse,
        response_model_exclude_none=True)
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
        query=converter(query),
        obj_id=vendor_id)

@vendors.get(
        '/{vendor_id}/info',
        tags=['jsonapi'],
        response_model=RelatedVendorInfoResponse,
        response_model_exclude_none=True)
async def related_info(
        token: VendorsPerm,
        session: NewSession,
        vendor_id: int,
        query: VendorQuery=Depends()
    ) -> RelatedVendorInfoResponse:
    return auth.secured_get_query(
        db=SCA_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['vendors'],
        resource=VENDORS_RESOURCE,
        query=converter(query),
        obj_id=vendor_id,
        relationship=False,
        related_resource='info')

@vendors.get(
        '/{vendor_id}/relationships/info',
        tags=['jsonapi'],
        response_model=VendorRelationshipsResponse,
        response_model_exclude_none=True)
async def info_relationships(
        token: VendorsPerm,
        session: NewSession,
        vendor_id: int,
        query: VendorQuery=Depends()
    ) -> VendorRelationshipsResponse:
    return auth.secured_get_query(
        db=SCA_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['vendors'],
        resource=VENDORS_RESOURCE,
        query=converter(query),
        obj_id=vendor_id,
        relationship=True,
        related_resource='info')

@vendors.post(
        '',
        tags=['jsonapi'],
        response_model=VendorResponse,
        response_model_exclude_none=True)
async def new_vendor(
        token: VendorsPerm,
        session: NewSession,
        body: NewVendor,
    ) -> VendorResponse:
    if auth.get_vendor_perm(token) >= auth.VendorPermPriority.sca_employee:
        return add_new_vendor(session=session, payload=body)
    raise HTTPException(status_code=401)

@vendors.patch(
        '/{vendor_id}',
        tags=['jsonapi'],
        response_model=VendorResponse,
        response_model_exclude_none=True)
async def modify_vendor(
        token: VendorsPerm,
        session: NewSession,
        vendor_id: int,
        body: VendorModification,
    ) -> VendorResponse:
    if auth.get_vendor_perm(token) >= auth.VendorPermPriority.sca_employee:
        return modify_existing_vendor(session, body, vendor_id)
    raise HTTPException(status_code=401)

@vendors.delete('/{vendor_id}', tags=['jsonapi'])
async def del_vendor(
        token: VendorsPerm,
        session: NewSession,
        vendor_id: int
    ) -> None:
    """Delete a Vendor as well as all accompanying vendor information"""
    if auth.get_vendor_perm(token) >= auth.VendorPermPriority.sca_admin:
        related_info = auth.secured_get_query(
            db=SCA_DB,
            session=session,
            token=token,
            auth_scheme=auth.Permissions['vendors'],
            resource=VENDORS_RESOURCE,
            query={},
            obj_id=vendor_id,
            relationship=True,
            related_resource='info'
        ).data
        related_info_ids: list[int] = [
            record['id']
            for record in related_info['data']
        ]
        for rec_id in related_info_ids:
            delete_vendor_info(session, rec_id)
        return delete_vendor(session, vendor_id)
    raise HTTPException(status_code=401)