
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorPricingByCustomerResp,
    VendorPricingByCustomerQuery,
    VendorPricingByCustomerQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorPricingByCustomer

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRICING_BY_CUSTOMER = VendorPricingByCustomer.__jsonapi_type_override__

vendor_pricing_by_customer = APIRouter(
    prefix=f"/{VENDOR_PRICING_BY_CUSTOMER}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorPricingByCustomerQueryJSONAPI)


@vendor_pricing_by_customer.get(
    "",
    response_model=VendorPricingByCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_collection(
    token: Token, session: NewSession, query: VendorPricingByCustomerQuery = Depends()
) -> VendorPricingByCustomerResp:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}",
    response_model=VendorPricingByCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_resource(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    query: VendorPricingByCustomerQuery = Depends(),
) -> VendorPricingByCustomerResp:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_id)
    )


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    query: VendorPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_id, "vendor-customers")
    )

@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/relationships/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    query: VendorPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_id, "vendor-customers", True)
    )

    
@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/vendor-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    query: VendorPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_id, "vendor-products")
    )

@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/relationships/vendor-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    query: VendorPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_id, "vendor-products", True)
    )

    
@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/vendor-pricing-by-customer-attrs",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_related_vendor_pricing_by_customer_attrs(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    query: VendorPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_id, "vendor-pricing-by-customer-attrs")
    )

@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/relationships/vendor-pricing-by-customer-attrs",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_relationships_vendor_pricing_by_customer_attrs(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    query: VendorPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_id, "vendor-pricing-by-customer-attrs", True)
    )

    
@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/vendor-pricing-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_related_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    query: VendorPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_id, "vendor-pricing-classes")
    )

@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/relationships/vendor-pricing-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_relationships_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    query: VendorPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_id, "vendor-pricing-classes", True)
    )

    
@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/vendor-pricing-by-customer-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_related_vendor_pricing_by_customer_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    query: VendorPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_id, "vendor-pricing-by-customer-changelog")
    )

@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/relationships/vendor-pricing-by-customer-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_relationships_vendor_pricing_by_customer_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    query: VendorPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_id, "vendor-pricing-by-customer-changelog", True)
    )

    
@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/customer-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_related_customer_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    query: VendorPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_id, "customer-pricing-by-customer")
    )

@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/relationships/customer-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_relationships_customer_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    query: VendorPricingByCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_id, "customer-pricing-by-customer", True)
    )

    

from app.v2.models import ModVendorPricingByCustomer

@vendor_pricing_by_customer.patch(
    "/{vendor_pricing_by_customer_id}",
    response_model=VendorPricingByCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    mod_data: ModVendorPricingByCustomer,
) -> VendorPricingByCustomerResp:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_pricing_by_customer_id,
                primary_id=mod_data.data.relationships.vendor_customers.data.id
            )
        )

        
@vendor_pricing_by_customer.delete(
    "/{vendor_pricing_by_customer_id}",
    tags=["jsonapi"],
)
async def del_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    vendor_customer_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_pricing_by_customer_id, primary_id=vendor_customer_id)
    )
    