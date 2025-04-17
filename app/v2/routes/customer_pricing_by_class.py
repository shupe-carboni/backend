from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import CustomerPricingByClassResp, NewCustomerPricingByClass
from app.jsonapi.sqla_models import CustomerPricingByClass

PARENT_PREFIX = "/vendors"
CUSTOMER_PRICING_BY_CLASS = CustomerPricingByClass.__jsonapi_type_override__

customer_pricing_by_class = APIRouter(
    prefix=f"/{CUSTOMER_PRICING_BY_CLASS}", tags=["v2"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@customer_pricing_by_class.post(
    "",
    response_model=CustomerPricingByClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_customer_pricing_by_class(
    token: Token,
    session: NewSession,
    new_obj: NewCustomerPricingByClass,
) -> CustomerPricingByClassResp:
    vendor_pricing_by_class_id = (
        new_obj.data.relationships.vendor_pricing_by_class.data.pop().id
    )
    vendor_id = new_obj.data.relationships.vendors.data.pop().id
    return (
        auth.VendorPricingByClassOperations(
            token, CustomerPricingByClass, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .post(
            session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=vendor_pricing_by_class_id,
        )
    )


@customer_pricing_by_class.delete(
    "/{customer_pricing_by_class_id}",
    tags=["jsonapi"],
)
async def del_customer_pricing_by_class(
    token: Token,
    session: NewSession,
    customer_pricing_by_class_id: int,
    vendor_pricing_by_class_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorPricingByClassOperations(
            token, CustomerPricingByClass, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(
            session,
            obj_id=customer_pricing_by_class_id,
            primary_id=vendor_pricing_by_class_id,
            hard_delete=True,
        )
    )


## NOT IMPLEMENTED ##


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
