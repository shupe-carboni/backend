from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorPricingByCustomerFutureResp,
    VendorPricingByCustomerFutureQuery,
    converters,
)
from app.jsonapi.sqla_models import VendorPricingByCustomerFuture

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRICING_BY_CUSTOMER_FUTURE = (
    VendorPricingByCustomerFuture.__jsonapi_type_override__
)

vendor_pricing_by_customer_future = APIRouter(
    prefix=f"/{VENDOR_PRICING_BY_CUSTOMER_FUTURE}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]
converter = converters[VendorPricingByCustomerFutureQuery]


@vendor_pricing_by_customer_future.get(
    "",
    response_model=VendorPricingByCustomerFutureResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_future_collection(
    token: Token,
    session: NewSession,
    query: VendorPricingByCustomerFutureQuery = Depends(),
) -> VendorPricingByCustomerFutureResp:
    return (
        auth.VendorPricingByCustomerOperations(
            token, VendorPricingByCustomerFuture, PARENT_PREFIX
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_pricing_by_customer_future.get(
    "/{vendor_pricing_by_customer_future_id}",
    response_model=VendorPricingByCustomerFutureResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_future_resource(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_future_id: int,
    query: VendorPricingByCustomerFutureQuery = Depends(),
) -> VendorPricingByCustomerFutureResp:
    return (
        auth.VendorPricingByCustomerOperations(
            token, VendorPricingByCustomerFuture, PARENT_PREFIX
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_future_id)
    )


@vendor_pricing_by_customer_future.get(
    "/{vendor_pricing_by_customer_future_id}/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_future_related_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_future_id: int,
    query: VendorPricingByCustomerFutureQuery = Depends(),
) -> None:
    return (
        auth.VendorPricingByCustomerOperations(
            token, VendorPricingByCustomerFuture, PARENT_PREFIX
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            vendor_pricing_by_customer_future_id,
            "vendor-pricing-by-customer",
        )
    )


@vendor_pricing_by_customer_future.get(
    "/{vendor_pricing_by_customer_future_id}/relationships/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_future_relationships_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_future_id: int,
    query: VendorPricingByCustomerFutureQuery = Depends(),
) -> None:
    return (
        auth.VendorPricingByCustomerOperations(
            token, VendorPricingByCustomerFuture, PARENT_PREFIX
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            vendor_pricing_by_customer_future_id,
            "vendor-pricing-by-customer",
            True,
        )
    )


from app.v2.models import (
    ModVendorPricingByCustomerFuture,
    NewVendorPricingByCustomerFuture,
)


@vendor_pricing_by_customer_future.post(
    "",
    response_model=VendorPricingByCustomerFutureResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_pricing_by_customer_future(
    token: Token,
    session: NewSession,
    new_data: NewVendorPricingByCustomerFuture,
) -> VendorPricingByCustomerFutureResp:
    vendor_id = new_data.data.relationships.vendors.data.pop().id
    return (
        auth.VendorPricingByCustomerOperations(
            token, VendorPricingByCustomerFuture, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session=session,
            data=new_data.model_dump(exclude_none=True, by_alias=True),
            primary_id=new_data.data.relationships.vendor_pricing_by_customer.data.pop().id,
        )
    )


@vendor_pricing_by_customer_future.patch(
    "/{vendor_pricing_by_customer_future_id}",
    response_model=VendorPricingByCustomerFutureResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_pricing_by_customer_future(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_future_id: int,
    mod_data: ModVendorPricingByCustomerFuture,
) -> VendorPricingByCustomerFutureResp:
    vendor_id = mod_data.data.relationships.vendors.data.pop().id
    return (
        auth.VendorPricingByCustomerOperations(
            token, VendorPricingByCustomerFuture, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_pricing_by_customer_future_id,
            primary_id=mod_data.data.relationships.vendor_pricing_by_customer.data.pop().id,
        )
    )


@vendor_pricing_by_customer_future.delete(
    "/{vendor_pricing_by_customer_future_id}",
    tags=["jsonapi"],
)
async def del_vendor_pricing_by_customer_future(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_future_id: int,
    vendor_pricing_by_customer_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorPricingByCustomerOperations(
            token, VendorPricingByCustomerFuture, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session,
            obj_id=vendor_pricing_by_customer_future_id,
            primary_id=vendor_pricing_by_customer_id,
        )
    )
