from enum import StrEnum
from datetime import datetime, date, time
from logging import getLogger
from functools import partial
from typing import Annotated, Callable, Union
from fastapi import Depends, HTTPException, status, UploadFile
from fastapi.routing import APIRouter
from enum import StrEnum

from app import auth
from app.admin.models import VendorId
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

PARENT_PREFIX = "/v2/vendors"
VENDOR_PREFIX = "/{vendor}"
VENDORS = Vendor.__jsonapi_type_override__

logger = getLogger("uvicorn.info")
pricing = APIRouter(prefix="", tags=["v2"])


def date_to_datetime(d: date) -> Optional[datetime]:
    if not d:
        return
    return datetime.combine(d, time(0, 0))


Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


class ReturnType(StrEnum):
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"


def generate_pricing_dl_link(
    vendor_id: VendorId, customer_id: int, callback: Callable
) -> str:
    resource_path = (
        f"/v2/vendors/{vendor_id}/vendor-customers/{customer_id}/pricing/download"
    )
    download_id = DownloadIDs.add_request(resource=resource_path, callback=callback)
    query = f"?download_id={download_id}"
    link = resource_path + query
    return link


@pricing.get(
    "/{vendor_id}/vendor-customers/{customer_id}/pricing",
    response_model=FullPricingWithLink,
    response_model_exclude_none=True,
    tags=["vendor customers", "pricing"],
)
async def vendor_customer_pricing(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    customer_id: int,
    effective_date: date = None,
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

    if effective_date:
        effective_date = date_to_datetime(effective_date)
    price_fetch = partial(fetch_pricing, session, vendor_id, customer_id)
    transform_ = partial(transform, customer, vendor_id, effective_date=effective_date)
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
                effective_date=effective_date,
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
                effective_date=effective_date,
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


@pricing.post(
    "/{vendor_id}/vendor-customers/{customer_id}/pricing",
    response_model=FullPricingWithLink,
    response_model_exclude_none=True,
    tags=["vendor customers", "pricing"],
)
async def new_vendor_customer_pricing(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    customer_id: int,
    templated_file: UploadFile,
    effective_date: date = None,
) -> FullPricingWithLink:
    """Add/update customer pricing for a vendor."""
    try:
        customer = (
            auth.VendorCustomerOperations(token, VendorCustomer, id=vendor_id)
            .allow_admin()
            .allow_sca()
            .allow_dev()
            .get(session, obj_id=customer_id)
        )
    except HTTPException as e:
        raise e

    return await vendor_customer_pricing(
        token,
        session,
        vendor_id,
        customer_id,
        None,
        ReturnType.JSON,
    )


@pricing.get(
    "/{vendor_id}/vendor-customers/{customer_id}/pricing/download",
    response_class=StreamingResponse,
    response_model=None,
    tags=["vendor customers", "pricing", "download"],
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
