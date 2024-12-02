from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.jsonapi.sqla_models import CustomerPricingByCustomer
from app.v2.models import NewCustomerPricingByCustomer, CustomerPricingByCustomerResp

PARENT_PREFIX = "/vendors"
CUSTOMER_PRICING_BY_CUSTOMER = CustomerPricingByCustomer.__jsonapi_type_override__

customer_pricing_by_customer = APIRouter(
    prefix=f"/{CUSTOMER_PRICING_BY_CUSTOMER}", tags=["v2"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@customer_pricing_by_customer.post(
    "",
    response_model=CustomerPricingByCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_customer_pricing_by_customer(
    token: Token,
    session: NewSession,
    new_obj: NewCustomerPricingByCustomer,
) -> CustomerPricingByCustomerResp:
    vendor_pricing_by_customer_id = (
        new_obj.data.relationships.vendor_pricing_by_customer.data.id
    )
    vendor_id = new_obj.data.relationships.vendors.data.id
    return (
        auth.VendorPricingByCustomerOperations(
            token, CustomerPricingByCustomer, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .post(
            session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=vendor_pricing_by_customer_id,
        )
    )


@customer_pricing_by_customer.delete(
    "/{customer_pricing_by_customer_id}",
    tags=["jsonapi"],
)
async def del_customer_pricing_by_customer(
    token: Token,
    session: NewSession,
    customer_pricing_by_customer_id: int,
    vendor_pricing_by_customer_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorPricingByCustomerOperations(
            token, CustomerPricingByCustomer, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(
            session,
            obj_id=customer_pricing_by_customer_id,
            primary_id=vendor_pricing_by_customer_id,
            hard_delete=True,
        )
    )


## NOT IMPLEMENTED ##


@customer_pricing_by_customer.get("", tags=["Not Implemented"])
async def customer_pricing_by_customer_collection(
    token: Token, session: NewSession
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@customer_pricing_by_customer.get(
    "/{customer_pricing_by_customer_id}", tags=["Not Implemented"]
)
async def customer_pricing_by_customer_resource(
    token: Token,
    session: NewSession,
    customer_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@customer_pricing_by_customer.get(
    "/{customer_pricing_by_customer_id}/vendor-pricing-by-customer",
    tags=["Not Implemented"],
)
async def customer_pricing_by_customer_related_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    customer_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@customer_pricing_by_customer.get(
    "/{customer_pricing_by_customer_id}/relationships/vendor-pricing-by-customer",
    tags=["Not Implemented"],
)
async def customer_pricing_by_customer_relationships_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    customer_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@customer_pricing_by_customer.get(
    "/{customer_pricing_by_customer_id}/users",
    tags=["Not Implemented"],
)
async def customer_pricing_by_customer_related_users(
    token: Token,
    session: NewSession,
    customer_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@customer_pricing_by_customer.get(
    "/{customer_pricing_by_customer_id}/relationships/users",
    tags=["Not Implemented"],
)
async def customer_pricing_by_customer_relationships_users(
    token: Token,
    session: NewSession,
    customer_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@customer_pricing_by_customer.patch(
    "/{customer_pricing_by_customer_id}", tags=["Not Implemented"]
)
async def mod_customer_pricing_by_customer(
    token: Token,
    session: NewSession,
    customer_pricing_by_customer_id: int,
    mod_data: None,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
