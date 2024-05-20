from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app import auth
from app.db import SCA_DB
from app.jsonapi.sqla_models import SCAVendorInfo, SCAVendor
from app.jsonapi.core_models import convert_query
from app.vendors.models import (
    VendorInfoResponse,
    NewVendorInfo,
    VendorInfoModification,
    VendorInfoQuery,
    VendorInfoQueryJSONAPI,
    RelatedVendorResponse,
)
from app.vendors.utils import (
    add_new_vendor_info,
    modify_existing_vendor_info,
    delete_vendor_info,
)

INFO_RESOURCE = SCAVendorInfo.__jsonapi_type_override__
VENDOR_RESOURCE = SCAVendor.__jsonapi_type_override__
vendors_info = APIRouter(prefix=f"/{INFO_RESOURCE}", tags=["vendors", "info"])

NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
VendorsPerm = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
converter = convert_query(VendorInfoQueryJSONAPI)


@vendors_info.get(
    "",
    response_model=VendorInfoResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def all_info(
    token: VendorsPerm, session: NewSession, query: VendorInfoQuery = Depends()
) -> VendorInfoResponse:
    return (
        auth.VendorOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session=session, resource=INFO_RESOURCE, query=converter(query))
    )


@vendors_info.get(
    "/{info_id}",
    response_model=VendorInfoResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def one_info(
    token: VendorsPerm,
    session: NewSession,
    info_id: int,
    query: VendorInfoQuery = Depends(),
) -> VendorInfoResponse:
    return (
        auth.VendorOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=INFO_RESOURCE,
            query=converter(query),
            obj_id=info_id,
        )
    )


@vendors_info.get(
    "/{info_id}/vendors",
    tags=["jsonapi"],
    response_model=RelatedVendorResponse,
    response_model_exclude_none=True,
)
async def info_related_vendor(
    token: VendorsPerm,
    session: NewSession,
    info_id: int,
    query: VendorInfoQuery = Depends(),
) -> RelatedVendorResponse:
    return (
        auth.VendorOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=INFO_RESOURCE,
            query=converter(query),
            obj_id=info_id,
            relationship=False,
            related_resource=VENDOR_RESOURCE,
        )
    )


@vendors_info.get(
    "/{info_id}/relationships/vendors",
    tags=["jsonapi"],
    response_model=VendorInfoResponse,
    response_model_exclude_none=True,
)
async def info_vendors_relationships(
    token: VendorsPerm,
    session: NewSession,
    info_id: int,
    query: VendorInfoQuery = Depends(),
) -> VendorInfoResponse:
    return (
        auth.VendorOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=INFO_RESOURCE,
            query=converter(query),
            obj_id=info_id,
            relationship=True,
            related_resource=VENDOR_RESOURCE,
        )
    )


@vendors_info.post(
    "",
    tags=["jsonapi"],
    response_model=VendorInfoResponse,
    response_model_exclude_none=True,
)
async def add_info(
    token: VendorsPerm,
    session: NewSession,
    body: NewVendorInfo,
) -> VendorInfoResponse:
    if token.permissions >= auth.Permissions.sca_employee:
        return add_new_vendor_info(session=session, payload=body)
    raise HTTPException(status_code=401)


@vendors_info.patch(
    "/{info_id}",
    tags=["jsonapi"],
    response_model=VendorInfoResponse,
    response_model_exclude_none=True,
)
async def modify_info(
    token: VendorsPerm,
    session: NewSession,
    info_id: int,
    body: VendorInfoModification,
) -> VendorInfoResponse:
    if token.permissions >= auth.Permissions.sca_employee:
        return modify_existing_vendor_info(
            session=session, payload=body, obj_id=info_id
        )
    raise HTTPException(status_code=401)


@vendors_info.delete("/{info_id}", tags=["jsonapi"])
async def delete_info(
    token: VendorsPerm,
    session: NewSession,
    info_id: int,
) -> None:
    if token.permissions >= auth.Permissions.sca_employee:
        return delete_vendor_info(session=session, obj_id=info_id)
    raise HTTPException(status_code=401)
