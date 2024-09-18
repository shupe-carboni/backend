from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session

# from app.RELATED_RESOURCE.models import
from app.v2.models import (
    CustomerPricingByClassResp,
    CustomerPricingByClassQuery,
    CustomerPricingByClassQueryJSONAPI,
)
from app.jsonapi.sqla_models import CustomerPricingByClass

PARENT_PREFIX = "/vendors"
CUSTOMER_PRICING_BY_CLASS = CustomerPricingByClass.__jsonapi_type_override__

customer_pricing_by_class = APIRouter(
    prefix=f"/{CUSTOMER_PRICING_BY_CLASS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]


@customer_pricing_by_class.get(
    "",
    tags=["Not Implemented"],
)
async def customer_pricing_by_class_collection(
    token: Token, session: NewSession
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@customer_pricing_by_class.get(
    "/{customer_pricing_by_class_id}",
    tags=["Not Implemented"],
)
async def customer_pricing_by_class_resource(
    token: Token,
    session: NewSession,
    customer_pricing_by_class_id: int,
) -> CustomerPricingByClassResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@customer_pricing_by_class.get(
    "/{customer_pricing_by_class_id}/vendor-pricing-by-class",
    tags=["Not Implemented"],
)
async def customer_pricing_by_class_related_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    customer_pricing_by_class_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@customer_pricing_by_class.get(
    "/{customer_pricing_by_class_id}/relationships/vendor-pricing-by-class",
    tags=["Not Implemented"],
)
async def customer_pricing_by_class_relationships_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    customer_pricing_by_class_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@customer_pricing_by_class.get(
    "/{customer_pricing_by_class_id}/users",
    tags=["Not Implemented"],
)
async def customer_pricing_by_class_related_users(
    token: Token,
    session: NewSession,
    customer_pricing_by_class_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@customer_pricing_by_class.get(
    "/{customer_pricing_by_class_id}/relationships/users",
    tags=["Not Implemented"],
)
async def customer_pricing_by_class_relationships_users(
    token: Token,
    session: NewSession,
    customer_pricing_by_class_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@customer_pricing_by_class.delete(
    "/{customer_pricing_by_class_id}",
    tags=["jsonapi"],
)
async def del_customer_pricing_by_clas(
    token: Token,
    session: NewSession,
    customer_pricing_by_class_id: int,
    vendor_pricing_by_class_id: int,
) -> None:
    return (
        auth.VendorPricingByClassOperations(
            token, CustomerPricingByClass, PARENT_PREFIX
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(
            session,
            obj_id=customer_pricing_by_class_id,
            primary_id=vendor_pricing_by_class_id,
        )
    )
