from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorProductAttrResourceResp,
    ModVendorProductAttr,
    NewVendorProductAttr,
)
from app.jsonapi.sqla_models import VendorProductAttr

PARENT_PREFIX = "/vendors"
VENDOR_PRODUCT_ATTRS = VendorProductAttr.__jsonapi_type_override__

vendor_product_attrs = APIRouter(prefix=f"/{VENDOR_PRODUCT_ATTRS}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_product_attrs.post(
    "",
    response_model=VendorProductAttrResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_product_attr(
    token: Token,
    session: NewSession,
    new_obj: NewVendorProductAttr,
) -> VendorProductAttrResourceResp:
    vendor_product_id = new_obj.data.relationships.vendor_products.data[0].id
    vendor_id = new_obj.data.relationships.vendors.data[0].id
    return (
        auth.VendorProductOperations(
            token, VendorProductAttr, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session=session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=vendor_product_id,
        )
    )


@vendor_product_attrs.patch(
    "/{vendor_product_attr_id}",
    response_model=VendorProductAttrResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_product_attr(
    token: Token,
    session: NewSession,
    vendor_product_attr_id: int,
    mod_data: ModVendorProductAttr,
) -> VendorProductAttrResourceResp:
    vendor_product_id = mod_data.data.relationships.vendor_products.data[0].id
    vendor_id = mod_data.data.relationships.vendors.data[0].id
    return (
        auth.VendorProductOperations(
            token, VendorProductAttr, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_product_attr_id,
            primary_id=vendor_product_id,
        )
    )


@vendor_product_attrs.delete(
    "/{vendor_product_attr_id}",
    tags=["jsonapi"],
)
async def del_vendor_product_attr(
    token: Token,
    session: NewSession,
    vendor_product_attr_id: int,
    vendor_product_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorProductOperations(
            token, VendorProductAttr, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(session, obj_id=vendor_product_attr_id, primary_id=vendor_product_id)
    )


## NOT IMPLEMENTED ##


@vendor_product_attrs.get(
    "",
    tags=["jsonapi"],
)
async def vendor_product_attr_collection(token: Token, session: NewSession) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_attrs.get(
    "/{vendor_product_attr_id}",
    tags=["jsonapi"],
)
async def vendor_product_attr_resource(
    token: Token,
    session: NewSession,
    vendor_product_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_attrs.get(
    "/{vendor_product_attr_id}/vendor-products",
    tags=["jsonapi"],
)
async def vendor_product_attr_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_product_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_attrs.get(
    "/{vendor_product_attr_id}/relationships/vendor-products",
    tags=["jsonapi"],
)
async def vendor_product_attr_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_product_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
