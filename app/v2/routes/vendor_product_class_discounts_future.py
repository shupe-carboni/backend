from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorProductClassDiscountFutureResp,
    VendorProductClassDiscountFutureQuery,
    converters,
)
from app.jsonapi.sqla_models import VendorProductClassDiscountFuture

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRODUCT_CLASS_DISCOUNTS_FUTURE = (
    VendorProductClassDiscountFuture.__jsonapi_type_override__
)

vendor_product_class_discounts_future = APIRouter(
    prefix=f"/{VENDOR_PRODUCT_CLASS_DISCOUNTS_FUTURE}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]
converter = converters[VendorProductClassDiscountFutureQuery]

# TODO enable price recalc on future pricing by new or modified discount futures


@vendor_product_class_discounts_future.get(
    "",
    response_model=VendorProductClassDiscountFutureResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discounts_future_collection(
    token: Token,
    session: NewSession,
    query: VendorProductClassDiscountFutureQuery = Depends(),
) -> VendorProductClassDiscountFutureResp:
    return (
        auth.VendorProductClassDiscountOperations(
            token, VendorProductClassDiscountFuture, PARENT_PREFIX
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_product_class_discounts_future.get(
    "/{vendor_product_class_discounts_future_id}",
    response_model=VendorProductClassDiscountFutureResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discounts_future_resource(
    token: Token,
    session: NewSession,
    vendor_product_class_discounts_future_id: int,
    query: VendorProductClassDiscountFutureQuery = Depends(),
) -> VendorProductClassDiscountFutureResp:
    return (
        auth.VendorProductClassDiscountOperations(
            token, VendorProductClassDiscountFuture, PARENT_PREFIX
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_class_discounts_future_id)
    )


@vendor_product_class_discounts_future.get(
    "/{vendor_product_class_discounts_future_id}/vendor-product-class-discounts",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discounts_future_related_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_product_class_discounts_future_id: int,
    query: VendorProductClassDiscountFutureQuery = Depends(),
) -> None:
    return (
        auth.VendorProductClassDiscountOperations(
            token, VendorProductClassDiscountFuture, PARENT_PREFIX
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            vendor_product_class_discounts_future_id,
            "vendor-product-class-discounts",
        )
    )


@vendor_product_class_discounts_future.get(
    "/{vendor_product_class_discounts_future_id}/relationships/vendor-product-class-discounts",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discounts_future_relationships_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_product_class_discounts_future_id: int,
    query: VendorProductClassDiscountFutureQuery = Depends(),
) -> None:
    return (
        auth.VendorProductClassDiscountOperations(
            token, VendorProductClassDiscountFuture, PARENT_PREFIX
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            vendor_product_class_discounts_future_id,
            "vendor-product-class-discounts",
            True,
        )
    )


from app.v2.models import (
    ModVendorProductClassDiscountFuture,
    NewVendorProductClassDiscountFuture,
)


@vendor_product_class_discounts_future.post(
    "",
    response_model=VendorProductClassDiscountFutureResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_product_class_discounts_future(
    token: Token,
    session: NewSession,
    new_data: NewVendorProductClassDiscountFuture,
) -> VendorProductClassDiscountFutureResp:
    vendor_id = new_data.data.relationships.vendors.data[0].id
    return (
        auth.VendorProductClassDiscountOperations(
            token, VendorProductClassDiscountFuture, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session=session,
            data=new_data.model_dump(exclude_none=True, by_alias=True),
            primary_id=new_data.data.relationships.vendor_product_class_discounts.data[
                0
            ].id,
        )
    )


@vendor_product_class_discounts_future.patch(
    "/{vendor_product_class_discounts_future_id}",
    response_model=VendorProductClassDiscountFutureResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_product_class_discounts_future(
    token: Token,
    session: NewSession,
    vendor_product_class_discounts_future_id: int,
    mod_data: ModVendorProductClassDiscountFuture,
) -> VendorProductClassDiscountFutureResp:
    vendor_id = mod_data.data.relationships.vendors.data[0].id
    return (
        auth.VendorProductClassDiscountOperations(
            token, VendorProductClassDiscountFuture, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_product_class_discounts_future_id,
            primary_id=mod_data.data.relationships.vendor_product_class_discounts.data[
                0
            ].id,
        )
    )


@vendor_product_class_discounts_future.delete(
    "/{vendor_product_class_discounts_future_id}",
    tags=["jsonapi"],
)
async def del_vendor_product_class_discounts_future(
    token: Token,
    session: NewSession,
    vendor_product_class_discounts_future_id: int,
    vendor_product_class_discounts_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorProductClassDiscountOperations(
            token, VendorProductClassDiscountFuture, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session,
            obj_id=vendor_product_class_discounts_future_id,
            primary_id=vendor_product_class_discounts_id,
        )
    )
