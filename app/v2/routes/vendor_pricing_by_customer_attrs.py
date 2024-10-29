from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorPricingByCustomerAttrResp,
    NewVendorPricingByCustomerAttr,
    ModVendorPricingByCustomerAttr,
)
from app.jsonapi.sqla_models import VendorPricingByCustomerAttr

PARENT_PREFIX = "/vendors"
VENDOR_PRICING_BY_CUSTOMER_ATTRS = VendorPricingByCustomerAttr.__jsonapi_type_override__

vendor_pricing_by_customer_attrs = APIRouter(
    prefix=f"/{VENDOR_PRICING_BY_CUSTOMER_ATTRS}", tags=["v2"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_pricing_by_customer_attrs.post(
    "",
    response_model=VendorPricingByCustomerAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_pricing_by_customer_attr(
    token: Token,
    session: NewSession,
    new_obj: NewVendorPricingByCustomerAttr,
) -> VendorPricingByCustomerAttrResp:
    vendor_pricing_by_customer_id = (
        new_obj.data.relationships.vendor_pricing_by_customer.data.id
    )
    vendor_id = new_obj.data.relationships.vendors.data.id
    return (
        auth.VendorPricingByCustomerOperations(
            token, VendorPricingByCustomerAttr, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=vendor_pricing_by_customer_id,
        )
    )


@vendor_pricing_by_customer_attrs.patch(
    "/{vendor_pricing_by_customer_attr_id}",
    response_model=VendorPricingByCustomerAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_pricing_by_customer_attr(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_attr_id: int,
    mod_obj: ModVendorPricingByCustomerAttr,
) -> VendorPricingByCustomerAttrResp:
    vendor_pricing_by_customer_id = (
        mod_obj.data.relationships.vendor_pricing_by_customer.data.id
    )
    vendor_id = mod_obj.data.relationships.vendors.data.id
    return (
        auth.VendorPricingByCustomerOperations(
            token, VendorPricingByCustomerAttr, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session,
            data=mod_obj.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_pricing_by_customer_attr_id,
            primary_id=vendor_pricing_by_customer_id,
        )
    )


@vendor_pricing_by_customer_attrs.delete(
    "/{vendor_pricing_by_customer_attr_id}",
    tags=["jsonapi"],
)
async def del_vendor_pricing_by_customer_attr(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_attr_id: int,
    vendor_pricing_by_customer_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorPricingByCustomerOperations(
            token, VendorPricingByCustomerAttr, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session,
            obj_id=vendor_pricing_by_customer_attr_id,
            primary_id=vendor_pricing_by_customer_id,
        )
    )


@vendor_pricing_by_customer_attrs.get("", tags=["Not Implemented"])
async def vendor_pricing_by_customer_attr_collection(
    token: Token,
    session: NewSession,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer_attrs.get(
    "/{vendor_pricing_by_customer_attr_id}", tags=["Not Implemented"]
)
async def vendor_pricing_by_customer_attr_resource(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer_attrs.get(
    "/{vendor_pricing_by_customer_attr_id}/vendor-pricing-by-customer",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_customer_attr_related_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer_attrs.get(
    "/{vendor_pricing_by_customer_attr_id}/relationships/vendor-pricing-by-customer",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_customer_attr_relationships_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
