from enum import StrEnum, auto
from logging import getLogger
from functools import partial
from typing import Annotated, Callable, Union
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from enum import StrEnum

from app import auth
from app.db import DB_V2, Session
from app.v2.models import *
from app.v2.pricing import transform, fetch_pricing
from app.admin.models import VendorId, FullPricingWithLink
from app.downloads import (
    XLSXFileResponse,
    FileResponse,
    DownloadIDs,
    StreamingResponse,
)
from app.jsonapi.sqla_models import Vendor
from app.adp.utils.workbook_factory import generate_program

PARENT_PREFIX = "/vendors"
VENDOR_PREFIX = "/{vendor}"
VENDORS = Vendor.__jsonapi_type_override__

logger = getLogger("uvicorn.info")
vendors = APIRouter(prefix=f"/{VENDORS}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


class ReturnType(StrEnum):
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"


class GetType(StrEnum):
    Collection = auto()
    Resource = auto()
    Related = auto()
    Relationships = auto()


def generate_pricing_dl_link(
    vendor_id: str, customer_id: int, callback: Callable
) -> str:
    resource_path = (
        f"/v2/vendors/{vendor_id}/vendor-customers/{customer_id}/pricing/download"
    )
    download_id = DownloadIDs.add_request(resource=resource_path, callback=callback)
    query = f"?download_id={download_id}"
    link = resource_path + query
    return link


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
    response_model=FullPricingWithLink,
    response_model_exclude_none=True,
    tags=["special", "pricing"],
)
async def vendor_customer_pricing(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    customer_id: int,
    return_type: ReturnType = ReturnType.JSON,
) -> FullPricingWithLink:
    """
    Getting pricing can be challenging to generalize on the front end, so logic here
    will do special method routing by-vendor if the request passes the auth
    check.

    Non-default return_types set in the query will still return JSON but only
    the download_link (no JSON pricing object).

    Execution of pricing file generation in this case is deferred
    to the return process in the route where the link is redeemed.
    """
    try:
        customer = (
            auth.VendorCustomerOperations(token, VendorCustomer, id=vendor_id)
            .allow_admin()
            .allow_sca()
            .allow_dev()
            .allow_customer("std")
            .get(session, obj_id=customer_id)
        )
    except HTTPException as e:
        raise e

    price_fetch = partial(fetch_pricing, session, vendor_id, customer_id)
    transform_ = partial(transform, customer, vendor_id)
    match vendor_id, return_type:
        # ReturnType.JSON: return pricing along with a download link to a CSV file
        # ReturnType.CSV: return a download link with deferred execution
        # ReturnType.XLSX: return a download link with deferred execution
        case VendorId.ATCO, ReturnType.JSON:
            remove_cols = ["fp_ean", "upc_code"]
            pricing = price_fetch(mode="both")
            cb = partial(transform_, pricing, remove_cols)
            dl_link = generate_pricing_dl_link(vendor_id, customer_id, cb)
            return FullPricingWithLink(download_link=dl_link, pricing=pricing)

        case VendorId.ATCO, ReturnType.CSV:
            remove_cols = ["fp_ean", "upc_code"]
            pricing = partial(price_fetch, mode="both")
            cb = partial(transform_, pricing, remove_cols)
            dl_link = generate_pricing_dl_link(vendor_id, customer_id, cb)
            return FullPricingWithLink(download_link=dl_link)

        case VendorId.ADP, ReturnType.JSON:
            remove_cols = None
            pricing = price_fetch(mode="customer")
            # ADP uses a special file generation method
            cb = partial(
                generate_program,
                session=session,
                customer_id=customer_id,
                stage=Stage.PROPOSED,
            )
            dl_link = generate_pricing_dl_link(vendor_id, customer_id, cb)
            return FullPricingWithLink(download_link=dl_link, pricing=pricing)

        case VendorId.ADP, ReturnType.XLSX:
            remove_cols = None
            # pricing = partial(fetch_pricing, mode="customer")
            # ADP uses a special file generation method
            cb = partial(
                generate_program,
                session=session,
                customer_id=customer_id,
                stage=Stage.PROPOSED,
            )
            dl_link = generate_pricing_dl_link(vendor_id, customer_id, cb)
            return FullPricingWithLink(download_link=dl_link)

        case VendorId.VYBOND, ReturnType.JSON:
            remove_cols = ["ucc", "upc"]
            pricing = price_fetch(mode="both", override_key="STATE_CPD")
            pivot = False
            cb = partial(transform_, pricing, remove_cols, pivot)
            dl_link = generate_pricing_dl_link(vendor_id, customer_id, cb)
            return FullPricingWithLink(download_link=dl_link, pricing=pricing)

        case VendorId.VYBOND, ReturnType.CSV:
            remove_cols = ["ucc", "upc"]
            pricing = partial(price_fetch, mode="both", override_key="STATE_CPD")
            pivot = False
            cb = partial(transform_, pricing, remove_cols, pivot)
            dl_link = generate_pricing_dl_link(vendor_id, customer_id, cb)
            return FullPricingWithLink(download_link=dl_link)

        case _:
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendors.get(
    "/{vendor_id}/vendor-customers/{customer_id}/pricing/download",
    response_class=StreamingResponse,
    response_model=None,
    tags=["special", "pricing", "download"],
)
async def download_price_file(
    vendor_id: VendorId, customer_id: int, download_id: str
) -> Union[FileResponse, XLSXFileResponse]:
    resource_path = (
        f"/v2/vendors/{vendor_id}/vendor-customers/{customer_id}/pricing/download"
    )
    dl_obj = DownloadIDs.use_download(
        resource=resource_path,
        id_value=download_id,
    )
    try:
        file = dl_obj.callback()
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    else:
        return file


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
