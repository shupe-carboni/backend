from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorProductClassDiscountResp,
    ModVendorProductClassDiscount,
    NewVendorProductClassDiscount,
)
from app.jsonapi.sqla_models import VendorProductClassDiscount

PARENT_PREFIX = "/vendors"
VENDOR_PRODUCT_CLASS_DISCOUNTS = VendorProductClassDiscount.__jsonapi_type_override__

vendor_product_class_discounts = APIRouter(
    prefix=f"/{VENDOR_PRODUCT_CLASS_DISCOUNTS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_product_class_discounts.post(
    "",
    response_model=VendorProductClassDiscountResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_product_class_discount(
    token: Token,
    session: NewSession,
    new_obj: NewVendorProductClassDiscount,
) -> VendorProductClassDiscountResp:
    return (
        auth.VendorCustomerOperations(token, VendorProductClassDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session=session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=new_obj.data.relationships.vendor_customers.data.id,
        )
    )


@vendor_product_class_discounts.patch(
    "/{vendor_product_class_discount_id}",
    response_model=VendorProductClassDiscountResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_product_class_discount(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
    mod_data: ModVendorProductClassDiscount,
) -> VendorProductClassDiscountResp:
    return (
        auth.VendorCustomerOperations(token, VendorProductClassDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_product_class_discount_id,
            primary_id=mod_data.data.relationships.vendor_customers.data.id,
        )
    )


@vendor_product_class_discounts.delete(
    "/{vendor_product_class_discount_id}",
    tags=["jsonapi"],
)
async def del_vendor_product_class_discount(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
    vendor_customer_id: int,
) -> None:
    return (
        auth.VendorCustomerOperations(token, VendorProductClassDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session,
            obj_id=vendor_product_class_discount_id,
            primary_id=vendor_customer_id,
        )
    )


@vendor_product_class_discounts.get("", tags=["jsonapi"])
async def vendor_product_class_discount_collection(
    token: Token,
    session: NewSession,
) -> VendorProductClassDiscountResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_resource(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> VendorProductClassDiscountResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/vendor-customers",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/relationships/vendor-customers",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/vendor-product-classes",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_related_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/relationships/vendor-product-classes",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_relationships_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/vendor-product-class-discounts-changelog",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_related_vendor_product_class_discounts_changelog(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/relationships/vendor-product-class-discounts-changelog",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_relationships_vendor_product_class_discounts_changelog(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
