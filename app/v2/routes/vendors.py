from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
from app.v2.models import (
    VendorResp,
    VendorQuery,
    VendorQueryJSONAPI,
    VendorsAttrResp,
    VendorsAttrRelResp,
    VendorProductResp,
    VendorProductRelResp,
    VendorProductClassResp,
    VendorProductClassRelResp,
    VendorPricingClassResp,
    VendorPricingClassRelResp,
    VendorCustomerResp,
    VendorCustomerRelResp,
)
from app.jsonapi.sqla_models import Vendor

PARENT_PREFIX = "/vendors/v2"
VENDORS = Vendor.__jsonapi_type_override__

vendors = APIRouter(prefix=f"/{VENDORS}", tags=["v2", ""])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorQueryJSONAPI)


@vendors.get(
    "",
    response_model=VendorResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_collection(
    token: Token, session: NewSession, query: VendorQuery = Depends()
) -> VendorResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendors.get(
    "/{vendor_id}",
    response_model=VendorResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_resource(
    token: Token,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> VendorResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_id)
    )


@vendors.get(
    "/{vendor_id}/vendors-attrs",
    response_model=VendorsAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_related_vendors_attrs(
    token: Token,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> VendorsAttrResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_id, "vendors-attrs")
    )


@vendors.get(
    "/{vendor_id}/relationships/vendors-attrs",
    response_model=VendorsAttrRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_relationships_vendors_attrs(
    token: Token,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> VendorsAttrRelResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_id, "vendors-attrs", True)
    )


@vendors.get(
    "/{vendor_id}/vendor-products",
    response_model=VendorProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> VendorProductResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_id, "vendor-products")
    )


@vendors.get(
    "/{vendor_id}/relationships/vendor-products",
    response_model=VendorProductRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> VendorProductRelResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_id, "vendor-products", True)
    )


@vendors.get(
    "/{vendor_id}/vendor-product-classes",
    response_model=VendorProductClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_related_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> VendorProductClassResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_id, "vendor-product-classes")
    )


@vendors.get(
    "/{vendor_id}/relationships/vendor-product-classes",
    response_model=VendorProductClassRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_relationships_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> VendorProductClassRelResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_id, "vendor-product-classes", True)
    )


@vendors.get(
    "/{vendor_id}/vendor-pricing-classes",
    response_model=VendorPricingClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_related_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> VendorPricingClassResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_id, "vendor-pricing-classes")
    )


@vendors.get(
    "/{vendor_id}/relationships/vendor-pricing-classes",
    response_model=VendorPricingClassRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_relationships_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> VendorPricingClassRelResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_id, "vendor-pricing-classes", True)
    )


@vendors.get(
    "/{vendor_id}/vendor-customers",
    response_model=VendorCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> VendorCustomerResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_id, "vendor-customers")
    )


@vendors.get(
    "/{vendor_id}/relationships/vendor-customers",
    response_model=VendorCustomerRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_id: int,
    query: VendorQuery = Depends(),
) -> VendorCustomerRelResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_id, "vendor-customers", True)
    )


@vendors.post("", tags=["Not Implemented"])
async def new_vendor(
    token: Token,
    session: NewSession,
    new_vendor: None,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


from app.v2.models import ModVendor


@vendors.patch(
    "/{vendor_id}",
    response_model=VendorResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor(
    token: Token,
    session: NewSession,
    vendor_id: int,
    mod_data: ModVendor,
) -> VendorResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_id,
        )
    )


@vendors.delete(
    "/{vendor_id}",
    tags=["jsonapi"],
)
async def del_vendor(
    token: Token,
    session: NewSession,
    vendor_id: int,
) -> None:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_id)
    )
