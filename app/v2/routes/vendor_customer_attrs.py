from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorCustomerAttrResp,
    ModVendorCustomerAttr,
    NewVendorCustomerAttr,
)
from app.jsonapi.sqla_models import VendorCustomerAttr

PARENT_PREFIX = "/vendors"
VENDOR_CUSTOMER_ATTRS = VendorCustomerAttr.__jsonapi_type_override__

vendor_customer_attrs = APIRouter(prefix=f"/{VENDOR_CUSTOMER_ATTRS}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_customer_attrs.post(
    "",
    response_model=VendorCustomerAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_customer_attr(
    token: Token,
    session: NewSession,
    new_obj: NewVendorCustomerAttr,
) -> VendorCustomerAttrResp:
    vendor_customer_id = new_obj.data.relationships.vendor_customers.data.id
    vendor_id = new_obj.data.relationships.vendors.data.id
    return (
        auth.VendorCustomerOperations(
            token, VendorCustomerAttr, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        # .allow_customer("admin")
        .patch(
            session=session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=vendor_customer_id,
        )
    )


@vendor_customer_attrs.patch(
    "/{vendor_customer_attr_id}",
    response_model=VendorCustomerAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_customer_attr(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
    mod_data: ModVendorCustomerAttr,
) -> VendorCustomerAttrResp:
    vendor_customer_id = mod_data.data.relationships.vendor_customers.data.id
    vendor_id = mod_data.data.relationships.vendors.data.id
    return (
        auth.VendorCustomerOperations(
            token, VendorCustomerAttr, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        # .allow_customer("admin")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_customer_attr_id,
            primary_id=vendor_customer_id,
        )
    )


@vendor_customer_attrs.delete(
    "/{vendor_customer_attr_id}",
    tags=["jsonapi"],
)
async def del_vendor_customer_attr(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
    vendor_customer_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorCustomerOperations(
            token, VendorCustomerAttr, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        # .allow_customer("admin")
        .delete(session, obj_id=vendor_customer_attr_id, primary_id=vendor_customer_id)
    )


## NOT IMPLEMENTED ##


@vendor_customer_attrs.get("", tags=["Not Implemented"])
async def vendor_customer_attr_collection(token: Token, session: NewSession) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_attrs.get("/{vendor_customer_attr_id}", tags=["Not Implemented"])
async def vendor_customer_attr_resource(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_attrs.get(
    "/{vendor_customer_attr_id}/vendor-customers", tags=["Not Implemented"]
)
async def vendor_customer_attr_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_attrs.get(
    "/{vendor_customer_attr_id}/relationships/vendor-customers",
    tags=["Not Implemented"],
)
async def vendor_customer_attr_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_attrs.get(
    "/{vendor_customer_attr_id}/vendor-customer-attrs-changelog",
    tags=["Not Implemented"],
)
async def vendor_customer_attr_related_vendor_customer_attrs_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_attrs.get(
    "/{vendor_customer_attr_id}/relationships/vendor-customer-attrs-changelog",
    tags=["Not Implemented"],
)
async def vendor_customer_attr_relationships_vendor_customer_attrs_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
