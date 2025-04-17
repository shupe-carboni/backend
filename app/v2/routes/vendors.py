from enum import StrEnum, auto
from logging import getLogger
from typing import Annotated
from fastapi import Depends, status, Response
from fastapi.routing import APIRouter
from enum import StrEnum

from app import auth
from app.admin.models import VendorId
from app.db import DB_V2, Session, S3
from app.v2.models import *
from app.admin.models import VendorId
from app.downloads import FileResponse
from app.jsonapi.sqla_models import Vendor

PARENT_PREFIX = "/v2/vendors"
VENDOR_PREFIX = "/{vendor}"
VENDORS = Vendor.__jsonapi_type_override__

logger = getLogger("uvicorn.info")
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
    response_model=VendorCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection, "vendors"],
)
async def vendor_collection(
    token: Token, session: NewSession, query: VendorQuery = Depends()
) -> VendorCollectionResp:
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
    response_model=VendorResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Resource, "vendors"],
)
async def vendor_resource(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    query: VendorQuery = Depends(),
) -> VendorResourceResp:
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
    response_model=VendorsAttrCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related, "vendors"],
)
async def vendor_related_vendors_attrs(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    query: VendorQuery = Depends(),
) -> VendorsAttrCollectionResp:
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
    tags=["jsonapi", GetType.Relationships, "vendors"],
)
async def vendor_relationships_vendors_attrs(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
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
    response_model=VendorProductCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection, "products"],
)
async def vendor_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    query: VendorProductQuery = Depends(),
) -> VendorProductCollectionResp:
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
    tags=["jsonapi", GetType.Relationships, "products"],
)
async def vendor_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
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
    response_model=VendorProductClassCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related, "products"],
)
async def vendor_related_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    query: VendorQuery = Depends(),
) -> VendorProductClassCollectionResp:
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
    tags=["jsonapi", GetType.Relationships, "products"],
)
async def vendor_relationships_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
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
    response_model=VendorPricingClassCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related, "pricing"],
)
async def vendor_related_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    query: VendorQuery = Depends(),
) -> VendorPricingClassCollectionResp:
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
    tags=["jsonapi", GetType.Relationships, "pricing"],
)
async def vendor_relationships_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
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
    response_model=VendorCustomerCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection, "vendor customers"],
)
async def vendor_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    query: VendorCustomerQuery = Depends(),
) -> VendorCustomerCollectionResp:
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
    tags=["jsonapi", GetType.Relationships, "vendor customers"],
)
async def vendor_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
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
    response_model=VendorsAttrsChangelogCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection, "vendors"],
)
async def vendors_attrs_changelog_collection(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    query: VendorsAttrsChangelogQuery = Depends(),
) -> VendorsAttrsChangelogCollectionResp:
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
    response_model=VendorProductAttrCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection, "products"],
)
async def vendors_products_attrs_collection(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    query: VendorProductAttrQuery = Depends(),
) -> VendorProductAttrCollectionResp:
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
    response_model=VendorPricingByCustomerCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection, "pricing"],
)
async def vendors_pricing_by_customer_collection(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    query: VendorPricingByCustomerQuery = Depends(),
) -> VendorPricingByCustomerCollectionResp:
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
    tags=["jsonapi", GetType.Collection, "pricing"],
)
async def customer_pricing_by_class_collection(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
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
    tags=["jsonapi", GetType.Collection, "pricing"],
)
async def customer_pricing_by_customer_collection(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
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
    response_model=VendorProductClassDiscountCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection, "discounts"],
)
async def vendors_product_class_discounts_collection(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    query: VendorProductClassDiscountQuery = Depends(),
) -> VendorProductClassDiscountCollectionResp:
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
    response_model=VendorCustomerPricingClassCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection, "pricing"],
)
async def vendor_customer_pricing_classes_collection(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    query: VendorCustomerPricingClassQuery = Depends(),
) -> VendorCustomerPricingClassCollectionResp:
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
    response_model=VendorQuoteCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Collection, "quotes"],
)
async def vendors_quotes_collection(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    query: VendorQuoteQuery = Depends(),
) -> VendorQuoteCollectionResp:
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
    response_model=VendorsAttrResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Resource, "vendors"],
)
async def vendors_attrs_related_object(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    attr_id: int,
    query: VendorsAttrQuery = Depends(),
) -> VendorsAttrResourceResp:
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
    response_model=VendorsAttrsChangelogCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related, "vendors"],
)
async def vendors_attrs_related_object_related_changelogs(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    attr_id: int,
    query: VendorsAttrQuery = Depends(),
) -> VendorsAttrsChangelogCollectionResp:
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
    response_model=VendorProductResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Resource, "products"],
)
async def vendors_producy_object(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    product_id: int,
    query: VendorProductQuery = Depends(),
) -> VendorProductResourceResp:
    prefix = PARENT_PREFIX + VENDOR_PREFIX.format(vendor=vendor_id)
    ret = (
        auth.VendorProductOperations(token, VendorProduct, prefix, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converters[VendorProductQuery](query), product_id)
    )
    return ret


@vendors.get(
    "/{vendor_id}/vendor-products/{product_id}/vendor-product-attrs",
    response_model=VendorProductAttrCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related, "products"],
)
async def vendors_product_related_object_attrs(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    product_id: int,
    query: VendorProductQuery = Depends(),
) -> VendorProductAttrCollectionResp:
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
    response_model=VendorCustomerResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Resource, "vendor customers"],
)
async def vendor_customer_obj(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> VendorCustomerResourceResp:
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
    "/{vendor_id}/vendor-customers/{customer_id}/vendor-pricing-by-customer",
    response_model=VendorPricingByCustomerCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related, "pricing", "vendor customers"],
)
async def vendor_customer_related_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> VendorPricingByCustomerCollectionResp:
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
    response_model=VendorProductClassDiscountCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related, "discounts", "vendor customers"],
)
async def vendor_customer_related_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> VendorProductClassDiscountCollectionResp:
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
    response_model=VendorCustomerPricingClassCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related, "vendor customers", "pricing"],
)
async def vendor_customer_related_customer_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> VendorCustomerPricingClassCollectionResp:
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
    response_model=VendorQuoteCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi", GetType.Related, "vendor customers", "quotes"],
)
async def vendor_customer_related_quotes(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    customer_id: int,
    query: VendorCustomerQuery = Depends(),
) -> VendorQuoteCollectionResp:
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
    response_model=VendorResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi", "vendors"],
)
async def new_vendor(
    token: Token,
    session: NewSession,
    new_vendor: NewVendor,
) -> VendorResourceResp:
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
    response_model=VendorResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi", "vendors"],
)
async def mod_vendor(
    token: Token,
    session: NewSession,
    vendor_id: str,
    mod_data: ModVendor,
) -> VendorResourceResp:
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
    tags=["jsonapi", "vendors"],
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


## download logo


@vendors.get("/{vendor_id}/logo", tags=["download"])
async def customer_logo_file(session: NewSession, vendor_id: VendorId):
    logo_key = DB_V2.execute(
        session,
        """SELECT logo_path from vendors where id = :id;""",
        dict(id=vendor_id),
    ).scalar_one_or_none()
    if logo_key:
        file = S3.get_file(logo_key)
        return FileResponse(
            content=file.file_content,
            media_type=file.file_mime,
            filename=file.file_name,
        )
    return Response(status.HTTP_204_NO_CONTENT)
