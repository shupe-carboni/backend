
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    CustomerPricingByCustomerResp,
    CustomerPricingByCustomerQuery,
    CustomerPricingByCustomerQueryJSONAPI,
)
from app.jsonapi.sqla_models import CustomerPricingByCustomer

PARENT_PREFIX = "/vendors/v2"
CUSTOMER_PRICING_BY_CUSTOMER = CustomerPricingByCustomer.__jsonapi_type_override__

customer_pricing_by_customer = APIRouter(
    prefix=f"/{CUSTOMER_PRICING_BY_CUSTOMER}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(CustomerPricingByCustomerQueryJSONAPI)


@customer_pricing_by_customer.get(
    "",
    response_model=CustomerPricingByCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_pricing_by_customer_collection(
    token: Token, session: NewSession, query: CustomerPricingByCustomerQuery = Depends()
) -> CustomerPricingByCustomerResp:
    return (
        auth.VOperations(token, CustomerPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@customer_pricing_by_customer.get(
    "/{customer_pricing_by_customer_id}",
    response_model=CustomerPricingByCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_pricing_by_customer_resource(
    token: Token,
    session: NewSession,
    customer_pricing_by_customer_id: int,
    query: CustomerPricingByCustomerQuery = Depends(),
) -> CustomerPricingByCustomerResp:
    return (
        auth.VOperations(token, CustomerPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_pricing_by_customer_id)
    )


@customer_pricing_by_customer.get(
    "/{customer_pricing_by_customer_id}/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_pricing_by_customer_related_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    customer_pricing_by_customer_id: int,
    query: CustomerPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, CustomerPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_pricing_by_customer_id, "vendor-pricing-by-customer")
    )

@customer_pricing_by_customer.get(
    "/{customer_pricing_by_customer_id}/relationships/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_pricing_by_customer_relationships_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    customer_pricing_by_customer_id: int,
    query: CustomerPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, CustomerPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_pricing_by_customer_id, "vendor-pricing-by-customer", True)
    )

    
@customer_pricing_by_customer.get(
    "/{customer_pricing_by_customer_id}/users",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_pricing_by_customer_related_users(
    token: Token,
    session: NewSession,
    customer_pricing_by_customer_id: int,
    query: CustomerPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, CustomerPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_pricing_by_customer_id, "users")
    )

@customer_pricing_by_customer.get(
    "/{customer_pricing_by_customer_id}/relationships/users",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_pricing_by_customer_relationships_users(
    token: Token,
    session: NewSession,
    customer_pricing_by_customer_id: int,
    query: CustomerPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, CustomerPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_pricing_by_customer_id, "users", True)
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
) -> None:
    return (
        auth.VOperations(token, CustomerPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=customer_pricing_by_customer_id, primary_id=vendor_pricing_by_customer_id)
    )
    