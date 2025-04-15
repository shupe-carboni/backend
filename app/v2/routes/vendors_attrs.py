from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import VendorsAttrResourceResp, ModVendorsAttr, NewVendorsAttr
from app.jsonapi.sqla_models import VendorsAttr

PARENT_PREFIX = "/vendors"
VENDORS_ATTRS = VendorsAttr.__jsonapi_type_override__

vendors_attrs = APIRouter(prefix=f"/{VENDORS_ATTRS}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendors_attrs.post(
    "",
    response_model=VendorsAttrResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendors_attr(
    token: Token,
    session: NewSession,
    new_obj: NewVendorsAttr,
) -> VendorsAttrResourceResp:
    vendor_id = new_obj.data.relationships.vendors.data.id
    return (
        auth.VendorOperations2(token, VendorsAttr, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session=session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=vendor_id,
        )
    )


@vendors_attrs.patch(
    "/{vendors_attr_id}",
    response_model=VendorsAttrResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendors_attr(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
    mod_data: ModVendorsAttr,
) -> VendorsAttrResourceResp:
    vendor_id = mod_data.data.relationships.vendors.data.id
    return (
        auth.VendorOperations2(token, VendorsAttr, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendors_attr_id,
            primary_id=vendor_id,
        )
    )


@vendors_attrs.delete(
    "/{vendors_attr_id}",
    tags=["jsonapi"],
)
async def del_vendors_attr(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorOperations2(token, VendorsAttr, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(session, obj_id=vendors_attr_id, primary_id=vendor_id)
    )


## NOT IMPLEMENTED ##


@vendors_attrs.get(
    "",
    tags=["jsonapi"],
)
async def vendors_attr_collection(token: Token, session: NewSession):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendors_attrs.get("/{vendors_attr_id}", tags=["jsonapi"])
async def vendors_attr_resource(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendors_attrs.get("/{vendors_attr_id}/vendors", tags=["jsonapi"])
async def vendors_attr_related_vendors(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendors_attrs.get("/{vendors_attr_id}/relationships/vendors", tags=["jsonapi"])
async def vendors_attr_relationships_vendors(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendors_attrs.get("/{vendors_attr_id}/vendors-attrs-changelog", tags=["jsonapi"])
async def vendors_attr_related_vendors_attrs_changelog(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendors_attrs.get(
    "/{vendors_attr_id}/relationships/vendors-attrs-changelog", tags=["jsonapi"]
)
async def vendors_attr_relationships_vendors_attrs_changelog(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
