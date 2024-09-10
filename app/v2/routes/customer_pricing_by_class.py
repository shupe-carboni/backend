
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    CustomerPricingByClassResp,
    CustomerPricingByClassQuery,
    CustomerPricingByClassQueryJSONAPI,
)
from app.jsonapi.sqla_models import CustomerPricingByClass

PARENT_PREFIX = "/vendors/v2"
CUSTOMER_PRICING_BY_CLASS = CustomerPricingByClass.__jsonapi_type_override__

customer_pricing_by_class = APIRouter(
    prefix=f"/{CUSTOMER_PRICING_BY_CLASS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(CustomerPricingByClassQueryJSONAPI)


@customer_pricing_by_class.get(
    "",
    response_model=CustomerPricingByClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_pricing_by_clas_collection(
    token: Token, session: NewSession, query: CustomerPricingByClassQuery = Depends()
) -> CustomerPricingByClassResp:
    return (
        auth.VOperations(token, CustomerPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@customer_pricing_by_class.get(
    "/{customer_pricing_by_clas_id}",
    response_model=CustomerPricingByClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_pricing_by_clas_resource(
    token: Token,
    session: NewSession,
    customer_pricing_by_clas_id: int,
    query: CustomerPricingByClassQuery = Depends(),
) -> CustomerPricingByClassResp:
    return (
        auth.VOperations(token, CustomerPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_pricing_by_clas_id)
    )


@customer_pricing_by_class.get(
    "/{customer_pricing_by_clas_id}/vendor-pricing-by-class",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_pricing_by_clas_related_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    customer_pricing_by_clas_id: int,
    query: CustomerPricingByClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, CustomerPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_pricing_by_clas_id, "vendor-pricing-by-class")
    )

@customer_pricing_by_class.get(
    "/{customer_pricing_by_clas_id}/relationships/vendor-pricing-by-class",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_pricing_by_clas_relationships_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    customer_pricing_by_clas_id: int,
    query: CustomerPricingByClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, CustomerPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_pricing_by_clas_id, "vendor-pricing-by-class", True)
    )

    
@customer_pricing_by_class.get(
    "/{customer_pricing_by_clas_id}/users",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_pricing_by_clas_related_users(
    token: Token,
    session: NewSession,
    customer_pricing_by_clas_id: int,
    query: CustomerPricingByClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, CustomerPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_pricing_by_clas_id, "users")
    )

@customer_pricing_by_class.get(
    "/{customer_pricing_by_clas_id}/relationships/users",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_pricing_by_clas_relationships_users(
    token: Token,
    session: NewSession,
    customer_pricing_by_clas_id: int,
    query: CustomerPricingByClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, CustomerPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_pricing_by_clas_id, "users", True)
    )

    
@customer_pricing_by_class.delete(
    "/{customer_pricing_by_clas_id}",
    tags=["jsonapi"],
)
async def del_customer_pricing_by_clas(
    token: Token,
    session: NewSession,
    customer_pricing_by_clas_id: int,
    vendor_pricing_by_clas_id: int,
) -> None:
    return (
        auth.VOperations(token, CustomerPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=customer_pricing_by_clas_id, primary_id=vendor_pricing_by_clas_id)
    )
    