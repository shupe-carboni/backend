from enum import StrEnum, auto
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import *

from app.jsonapi.sqla_models import Vendor

PARENT_PREFIX = "/vendors"
VENDOR_PREFIX = "/{vendor}"
VENDORS = Vendor.__jsonapi_type_override__

vendors = APIRouter(prefix=f"/{VENDORS}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


class GetType(StrEnum):
    Collection = auto()
    Resource = auto()
    Related = auto()
    Relationships = auto()


@vendors.get(
    "",
    response_model=VendorResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection],
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
        .get(session, converters[VendorQuery](query))
    )


@vendors.get(
    "/{vendor_id}",
    response_model=VendorResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Resource],
)
async def vendor_resource(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorQuery = Depends(),
) -> VendorResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converters[VendorQuery](query), vendor_id)
    )


@vendors.get(
    "/{vendor_id}/vendors-attrs",
    response_model=VendorsAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related],
)
async def vendor_related_vendors_attrs(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorQuery = Depends(),
) -> VendorsAttrResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converters[VendorQuery](query), vendor_id, "vendors-attrs")
    )


@vendors.get(
    "/{vendor_id}/relationships/vendors-attrs",
    response_model=VendorsAttrRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Relationships],
)
async def vendor_relationships_vendors_attrs(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorQuery = Depends(),
) -> VendorsAttrRelResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converters[VendorQuery](query), vendor_id, "vendors-attrs", True)
    )


@vendors.get(
    "/{vendor_id}/vendor-products",
    response_model=VendorProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection],
)
async def vendor_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorProductQuery = Depends(),
) -> VendorProductResp:
    return (
        auth.VendorOperations2(token, VendorProduct, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converters[VendorProductQuery](query))
    )


@vendors.get(
    "/{vendor_id}/relationships/vendor-products",
    response_model=VendorProductRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Relationships],
)
async def vendor_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorQuery = Depends(),
) -> VendorProductRelResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session, converters[VendorQuery](query), vendor_id, "vendor-products", True
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-product-classes",
    response_model=VendorProductClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related],
)
async def vendor_related_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorQuery = Depends(),
) -> VendorProductClassResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session, converters[VendorQuery](query), vendor_id, "vendor-product-classes"
        )
    )


@vendors.get(
    "/{vendor_id}/relationships/vendor-product-classes",
    response_model=VendorProductClassRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Relationships],
)
async def vendor_relationships_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorQuery = Depends(),
) -> VendorProductClassRelResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorQuery](query),
            vendor_id,
            "vendor-product-classes",
            True,
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-pricing-classes",
    response_model=VendorPricingClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related],
)
async def vendor_related_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorQuery = Depends(),
) -> VendorPricingClassResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session, converters[VendorQuery](query), vendor_id, "vendor-pricing-classes"
        )
    )


@vendors.get(
    "/{vendor_id}/relationships/vendor-pricing-classes",
    response_model=VendorPricingClassRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Relationships],
)
async def vendor_relationships_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorQuery = Depends(),
) -> VendorPricingClassRelResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorQuery](query),
            vendor_id,
            "vendor-pricing-classes",
            True,
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-customers",
    response_model=VendorCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection],
)
async def vendor_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorCustomerQuery = Depends(),
) -> VendorCustomerResp:
    # id must be the kwarg to filter on Vendors as the primary resource due to
    # how sqlalchemy aliases parameter names that I need to bind to.
    return (
        auth.VendorOperations2(token, VendorCustomer, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converters[VendorCustomerQuery](query))
    )


@vendors.get(
    "/{vendor_id}/relationships/vendor-customers",
    response_model=VendorCustomerRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Relationships],
)
async def vendor_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorQuery = Depends(),
) -> VendorCustomerRelResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session, converters[VendorQuery](query), vendor_id, "vendor-customers", True
        )
    )


# chained GETs - static collections
# NOTE - beyond the secondary level, a filtering criteria is needed on collections


@vendors.get(
    "/{vendor_id}/vendors-attrs/vendors-attrs-changelog",
    response_model=VendorsAttrsChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection],
)
async def vendors_attrs_changelog_collection(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorsAttrsChangelogQuery = Depends(),
) -> VendorsAttrsChangelogResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorsAttrOperations(
            token, VendorsAttrsChangelog, prefix, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorsAttrsChangelogQuery](query),
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-products/vendor-product-attrs",
    response_model=VendorProductAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection],
)
async def vendors_products_attrs_collection(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorProductAttrQuery = Depends(),
) -> VendorProductAttrResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorProductOperations(
            token, VendorProductAttr, prefix, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorProductAttrQuery](query),
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-customers/vendor-pricing-by-customer",
    response_model=VendorPricingByCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection],
)
async def vendors_pricing_by_customer_collection(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorPricingByCustomerQuery = Depends(),
) -> VendorPricingByCustomerResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorCustomerOperations(
            token, VendorPricingByCustomer, prefix, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorPricingByCustomerQuery](query),
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-customers/customer-pricing-by-class",
    response_model=CustomerPricingByClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection],
)
async def customer_pricing_by_class_collection(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: CustomerPricingByClassQuery = Depends(),
) -> CustomerPricingByClassResp:
    """Customer 'favorites' within the vendor's price assignments by class/tier
    assigned to the customer account(s) with which the user is associated."""
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorPricingByClassOperations(
            token, CustomerPricingByClass, prefix, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[CustomerPricingByClassQuery](query),
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-customers/customer-pricing-by-customer",
    response_model=CustomerPricingByCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection],
)
async def customer_pricing_by_customer_collection(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: CustomerPricingByCustomerQuery = Depends(),
) -> CustomerPricingByCustomerResp:
    """Customer 'favorites' within the vendor's price assignments directly
    to the customer account(s) with which the user is associated."""
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorCustomerOperations(
            token, CustomerPricingByCustomer, prefix, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[CustomerPricingByCustomerQuery](query),
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-customers/vendor-product-class-discounts",
    response_model=VendorProductClassDiscountResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection],
)
async def vendors_product_class_discounts_collection(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorProductClassDiscountQuery = Depends(),
) -> VendorProductClassDiscountResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorCustomerOperations(
            token, VendorProductClassDiscount, prefix, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorProductClassDiscountQuery](query),
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-customers/vendor-customer-pricing-classes",
    response_model=VendorCustomerPricingClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection],
)
async def vendor_customer_pricing_classes_collection(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorCustomerPricingClassQuery = Depends(),
) -> VendorCustomerPricingClassResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorCustomerOperations(
            token, VendorCustomerPricingClass, prefix, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorCustomerPricingClassQuery](query),
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-customers/vendor-quotes",
    response_model=VendorQuoteResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection],
)
async def vendors_quotes_collection(
    token: Token,
    session: NewSession,
    vendor_id: str,
    query: VendorQuoteQuery = Depends(),
) -> VendorQuoteResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorCustomerOperations(token, VendorQuote, prefix, vendor_id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorQuoteQuery](query),
        )
    )


# chained GETs - dynamic resource access


@vendors.get(
    "/{vendor_id}/vendors-attrs/{attr_id}",
    response_model=VendorsAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Resource],
)
async def vendors_attrs_related_object(
    token: Token,
    session: NewSession,
    vendor_id: str,
    attr_id: int,
    query: VendorsAttrQuery = Depends(),
) -> VendorsAttrResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorOperations2(token, VendorsAttr, prefix)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorsAttrQuery](query),
            attr_id,
        )
    )


@vendors.get(
    "/{vendor_id}/vendors-attrs/{attr_id}/vendors-attrs-changelog",
    response_model=VendorsAttrsChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related],
)
async def vendors_attrs_related_object_related_changelogs(
    token: Token,
    session: NewSession,
    vendor_id: str,
    attr_id: int,
    query: VendorsAttrQuery = Depends(),
) -> VendorCustomerAttrChangelogResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorsAttrOperations(token, VendorsAttr, prefix)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorsAttrQuery](query),
            attr_id,
            "vendors-attrs-changelog",
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-products/{product_id}",
    response_model=VendorProductAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Resource],
)
async def vendors_product_related_object(
    token: Token,
    session: NewSession,
    vendor_id: str,
    product_id: int,
    query: VendorProductAttrQuery = Depends(),
) -> VendorProductAttrResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorProductOperations(
            token, VendorProductAttr, prefix, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converters[VendorProductAttrQuery](query), product_id)
    )


@vendors.get(
    "/{vendor_id}/vendor-products/{product_id}/vendor-product-attrs",
    response_model=VendorProductAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related],
)
async def vendors_product_related_object_attrs(
    token: Token,
    session: NewSession,
    vendor_id: str,
    product_id: int,
    query: VendorProductQuery = Depends(),
) -> VendorProductAttrResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorProductOperations(token, VendorProduct, prefix, vendor_id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorProductQuery](query),
            product_id,
            "vendor-product-attrs",
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-customers/{customer_id}",
    response_model=VendorCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Resource],
)
async def vendor_customer_obj(
    token: Token,
    session: NewSession,
    vendor_id: str,
    customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> VendorCustomerResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorCustomerOperations(
            token, VendorCustomer, prefix, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converters[VendorCustomerQuery](query), customer_id)
    )


@vendors.get(
    "/{vendor_id}/vendor-customers/{customer_id}/pricing",
    response_model=None,
    response_model_exclude_none=True,
    tags=["special"],
)
async def vendor_customer_obj(
    token: Token,
    session: NewSession,
    vendor_id: str,
    customer_id: int,
) -> None:
    # TODO SET UP CUSTOM LOGIC TO GET CUSTOMER PRICING
    """
    Getting pricing can be challenging to generalize on the front end, so logic here
    will do special method routing by-vendor one if the request passes the auth
    check
    """
    try:
        (
            auth.VendorCustomerOperations(token, VendorCustomer, id=vendor_id)
            .allow_admin()
            .allow_sca()
            .allow_dev()
            .allow_customer("std")
            .get(session, obj_id=customer_id)
        )
    except HTTPException as e:
        raise e

    ### REST OF LOCIC ###

    return


@vendors.get(
    "/{vendor_id}/vendor-customers/{customer_id}/vendor-pricing-by-customer",
    response_model=VendorPricingByCustomerResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related],
)
async def vendor_customer_related_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_id: str,
    customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> VendorPricingByCustomerResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorCustomerOperations(
            token, VendorCustomer, prefix, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorCustomerQuery](query),
            customer_id,
            "vendor-pricing-by-customer",
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-customers/{customer_id}/vendor-product-class-discounts",
    response_model=VendorProductClassDiscountResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related],
)
async def vendor_customer_related_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_id: str,
    customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> VendorProductClassDiscountResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorCustomerOperations(
            token, VendorCustomer, prefix, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorCustomerQuery](query),
            customer_id,
            "vendor-product-class-discounts",
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-customers/{customer_id}/vendor-customer-pricing-classes",
    response_model=VendorCustomerPricingClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related],
)
async def vendor_customer_related_customer_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_id: str,
    customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> VendorCustomerPricingClassResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorCustomerOperations(
            token, VendorCustomer, prefix, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorCustomerQuery](query),
            customer_id,
            "vendor-customer-pricing-classes",
        )
    )


@vendors.get(
    "/{vendor_id}/vendor-customers/{customer_id}/vendor-quotes",
    response_model=VendorQuoteResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related],
)
async def vendor_customer_related_quotes(
    token: Token,
    session: NewSession,
    vendor_id: str,
    customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> VendorQuoteResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    return (
        auth.VendorCustomerOperations(
            token, VendorCustomer, prefix, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converters[VendorCustomerQuery](query),
            customer_id,
            "vendor-quotes",
        )
    )


@vendors.post(
    "",
    response_model=VendorResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor(
    token: Token,
    session: NewSession,
    new_vendor: NewVendor,
) -> VendorResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(session, new_vendor.model_dump(exclude_none=True, by_alias=True))
    )


# modifications to vendors

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
    vendor_id: str,
    mod_data: ModVendor,
) -> VendorResp:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX, vendor_id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
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
    vendor_id: str,
) -> None:
    return (
        auth.VendorOperations2(token, Vendor, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(session, obj_id=vendor_id)
    )
