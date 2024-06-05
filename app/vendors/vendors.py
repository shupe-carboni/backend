from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app import auth
from app.db import SCA_DB
from app.jsonapi.sqla_models import SCAVendor
from app.jsonapi.core_models import convert_query
from app.vendors.models import (
    VendorResponse,
    VendorQuery,
    VendorQueryJSONAPI,
    RelatedVendorInfoResponse,
    VendorRelationshipsResponse,
    NewVendor,
    VendorModification,
)
from app.vendors.vendors_info import delete_info

VENDORS_RESOURCE = SCAVendor.__jsonapi_type_override__
vendors = APIRouter(prefix=f"/{VENDORS_RESOURCE}", tags=["vendors"])

NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
VendorsPerm = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
converter = convert_query(VendorQueryJSONAPI)


@vendors.get(
    "",
    response_model=VendorResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_collection(
    token: VendorsPerm, session: NewSession, query: VendorQuery = Depends()
) -> VendorResponse:
    return (
        auth.VendorOperations(token, VENDORS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session=session, query=converter(query))
    )


@vendors.get(
    "/{vendor_id}",
    response_model=VendorResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor(
    token: VendorsPerm,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> VendorResponse:
    return (
        auth.VendorOperations(token, VENDORS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            query=converter(query),
            obj_id=vendor_id,
        )
    )


@vendors.get(
    "/{vendor_id}/info",
    response_model=RelatedVendorInfoResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def related_info(
    token: VendorsPerm,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> RelatedVendorInfoResponse:
    return (
        auth.VendorOperations(token, VENDORS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            query=converter(query),
            obj_id=vendor_id,
            relationship=False,
            related_resource="info",
        )
    )


@vendors.get(
    "/{vendor_id}/relationships/info",
    tags=["jsonapi"],
    response_model=VendorRelationshipsResponse,
    response_model_exclude_none=True,
)
async def info_relationships(
    token: VendorsPerm,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> VendorRelationshipsResponse:
    return (
        auth.VendorOperations(token, VENDORS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            query=converter(query),
            obj_id=vendor_id,
            relationship=True,
            related_resource="info",
        )
    )


@vendors.post(
    "",
    tags=["jsonapi"],
    response_model=VendorResponse,
    response_model_exclude_none=True,
)
async def new_vendor(
    token: VendorsPerm,
    session: NewSession,
    body: NewVendor,
) -> VendorResponse:
    return (
        auth.VendorOperations(token, VENDORS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session=session,
            data=body.model_dump(exclude_none=True, by_alias=True),
        )
    )


@vendors.patch(
    "/{vendor_id}",
    tags=["jsonapi"],
    response_model=VendorResponse,
    response_model_exclude_none=True,
)
async def modify_vendor(
    token: VendorsPerm,
    session: NewSession,
    vendor_id: int,
    body: VendorModification,
) -> VendorResponse:
    return (
        auth.VendorOperations(token, VENDORS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=body.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_id,
        )
    )


@vendors.delete("/{vendor_id}", tags=["jsonapi"])
async def del_vendor(token: VendorsPerm, session: NewSession, vendor_id: int) -> None:
    """Delete a Vendor as well as all accompanying vendor information"""
    related_info = await info_relationships(token, session, vendor_id, VendorQuery())
    related_info_ids: list[int] = [record["id"] for record in related_info["data"]]
    for rec_id in related_info_ids:
        # will raise an error if the action is not permitted, an all or nothing setup
        # so it should fail on the first record or not at all
        await delete_info(token, session, rec_id, vendor_id)
    return (
        auth.VendorOperations(token, VENDORS_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session=session,
            obj_id=vendor_id,
        )
    )
