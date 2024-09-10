
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorCustomerResp,
    VendorCustomerQuery,
    VendorCustomerQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorCustomer

PARENT_PREFIX = "/vendors/v2"
VENDOR_CUSTOMERS = VendorCustomer.__jsonapi_type_override__

vendor_customers = APIRouter(
    prefix=f"/{VENDOR_CUSTOMERS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorCustomerQueryJSONAPI)


@vendor_customers.get(
    "",
    response_model=VendorCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_collection(
    token: Token, session: NewSession, query: VendorCustomerQuery = Depends()
) -> VendorCustomerResp:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_customers.get(
    "/{vendor_customer_id}",
    response_model=VendorCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_resource(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> VendorCustomerResp:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id)
    )


@vendor_customers.get(
    "/{vendor_customer_id}/vendors",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_related_vendors(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendors")
    )

@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendors",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_relationships_vendors(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendors", True)
    )

    
@vendor_customers.get(
    "/{vendor_customer_id}/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_related_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-pricing-by-customer")
    )

@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_relationships_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-pricing-by-customer", True)
    )

    
@vendor_customers.get(
    "/{vendor_customer_id}/vendor-customer-pricing-classes-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_related_vendor_customer_pricing_classes_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-customer-pricing-classes-changelog")
    )

@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-customer-pricing-classes-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_relationships_vendor_customer_pricing_classes_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-customer-pricing-classes-changelog", True)
    )

    
@vendor_customers.get(
    "/{vendor_customer_id}/vendor-customer-pricing-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_related_vendor_customer_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-customer-pricing-classes")
    )

@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-customer-pricing-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_relationships_vendor_customer_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-customer-pricing-classes", True)
    )

    
@vendor_customers.get(
    "/{vendor_customer_id}/vendor-customer-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_related_vendor_customer_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-customer-changelog")
    )

@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-customer-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_relationships_vendor_customer_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-customer-changelog", True)
    )

    
@vendor_customers.get(
    "/{vendor_customer_id}/vendor-quotes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_related_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-quotes")
    )

@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-quotes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_relationships_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-quotes", True)
    )

    
@vendor_customers.get(
    "/{vendor_customer_id}/vendor-customer-attrs",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_related_vendor_customer_attrs(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-customer-attrs")
    )

@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-customer-attrs",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_relationships_vendor_customer_attrs(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-customer-attrs", True)
    )

    
@vendor_customers.get(
    "/{vendor_customer_id}/vendor-product-class-discounts",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_related_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-product-class-discounts")
    )

@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-product-class-discounts",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_relationships_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "vendor-product-class-discounts", True)
    )

    
@vendor_customers.get(
    "/{vendor_customer_id}/customer-location-mapping",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_related_customer_location_mapping(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "customer-location-mapping")
    )

@vendor_customers.get(
    "/{vendor_customer_id}/relationships/customer-location-mapping",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_relationships_customer_location_mapping(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_id, "customer-location-mapping", True)
    )

    

from app.v2.models import ModVendorCustomer

@vendor_customers.patch(
    "/{vendor_customer_id}",
    response_model=VendorCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_customer(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    mod_data: ModVendorCustomer,
) -> VendorCustomerResp:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_customer_id,
                primary_id=mod_data.data.relationships.vendors.data.id
            )
        )

        
@vendor_customers.delete(
    "/{vendor_customer_id}",
    tags=["jsonapi"],
)
async def del_vendor_customer(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    vendor_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorCustomer, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_customer_id, primary_id=vendor_id)
    )
    