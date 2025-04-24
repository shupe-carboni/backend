from io import BytesIO
from datetime import datetime, date, time
from logging import getLogger
from functools import partial
from typing import Annotated, Callable, Union
from fastapi import Depends, HTTPException, status, UploadFile, BackgroundTasks
from fastapi.routing import APIRouter
from enum import StrEnum
import openpyxl

from app import auth
from app.admin.models import VendorId
from app.db import DB_V2, Session
from app.v2.models import *
from app.v2.pricing import transform, fetch_pricing
from app.v2.routes.vendor_product_class_discounts import (
    new_vendor_product_class_discount,
    mod_vendor_product_class_discount,
)
from app.admin.models import (
    VendorId,
    FullPricingWithLink,
    PriceTemplateSheetColumns,
    PriceTemplateSheet,
    PriceTemplateModels,
    ProductCategoryDiscount as ProductCategoryDiscountDTO,
    ProductDiscount as ProductDiscountDTO,
    CustomerPrice as CustomerPriceDTO,
    CustomerPriceCategory as CustomerPriceCategoryDTO,
)
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

        case VendorId.FRIEDRICH, ReturnType.JSON:
            remove_cols = None
            pricing = price_fetch(mode="both")
            pivot = False
            cb = partial(transform_, pricing, remove_cols, pivot)
            dl_link = generate_pricing_dl_link(vendor_id, customer_id, cb)
            return FullPricingWithLink(download_link=dl_link, pricing=pricing)

        case VendorId.FRIEDRICH, ReturnType.CSV:
            remove_cols = None
            pricing = partial(price_fetch, mode="both")
            pivot = False
            cb = partial(transform_, pricing, remove_cols, pivot)
            dl_link = generate_pricing_dl_link(vendor_id, customer_id, cb)
            return FullPricingWithLink(download_link=dl_link, pricing=pricing)

        case _:
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@pricing.post(
    "/{vendor_id}/vendor-customers/{customer_id}/pricing",
    response_model=FullPricingWithLink,
    response_model_exclude_none=True,
    tags=["vendor customers", "pricing"],
)
async def upsert_vendor_customer_pricing_from_file(
    token: Token,
    session: NewSession,
    vendor_id: VendorId,
    customer_id: int,
    templated_file: UploadFile,
    effective_date: date = datetime.today().date(),
) -> FullPricingWithLink:
    """Upsert customer pricing for a vendor."""
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

    file_data = BytesIO(await templated_file.read())
    parsed_data = parse_pricing_template(file_data)
    errors: dict[str, list[dict[str, str]]] = {}
    updates: dict[str, list[dict[str, str]]] = {}
    inserts: dict[str, list[dict[str, str]]] = {}
    for record_type, records in parsed_data.items():
        match record_type:
            case PriceTemplateSheet.CUSTOMER_PRICING:
                record: CustomerPriceDTO
                errors.setdefault(record_type, [])
                updates.setdefault(record_type, [])
                inserts.setdefault(record_type, [])
                ...
            case PriceTemplateSheet.PRODUCT_CATEGORY_DISCOUNTS:
                errors.setdefault(record_type, [])
                updates.setdefault(record_type, [])
                inserts.setdefault(record_type, [])
                for record in records:
                    record_: ProductCategoryDiscountDTO = record
                    try:
                        base_class_id = record_.get_base_price_category_id(
                            session, vendor_id
                        )
                        label_class_id = record_.get_label_price_category_id(
                            session, vendor_id
                        )
                        product_class_id = record_.get_product_category_id(
                            session, vendor_id
                        )
                        data = NewVendorProductClassDiscountRObj(
                            type="vendor-product-class-discounts",
                            attributes=VendorProductClassDiscountAttrs(
                                discount=record_.discount,
                                effective_date=effective_date,
                            ),
                            relationships=VendorProductClassDiscountRels(
                                vendors=JSONAPIRelationships(
                                    data=[
                                        JSONAPIResourceIdentifier(
                                            id=vendor_id.value, type="vendors"
                                        )
                                    ]
                                ),
                                vendor_customers=JSONAPIRelationships(
                                    data=[
                                        JSONAPIResourceIdentifier(
                                            id=customer_id, type="vendor-customers"
                                        )
                                    ]
                                ),
                                base_price_classes=JSONAPIRelationships(
                                    data=[
                                        JSONAPIResourceIdentifier(
                                            id=base_class_id,
                                            type="base-price-classes",
                                        )
                                    ]
                                ),
                                label_price_classes=JSONAPIRelationships(
                                    data=[
                                        JSONAPIResourceIdentifier(
                                            id=label_class_id,
                                            type="label-price-classes",
                                        )
                                    ]
                                ),
                                vendor_product_classes=JSONAPIRelationships(
                                    data=[
                                        JSONAPIResourceIdentifier(
                                            id=product_class_id,
                                            type="vendor-product-classes",
                                        )
                                    ]
                                ),
                            ),
                        )
                    except Exception as e:
                        errors[record_type].append(
                            {"record": record_.model_dump(), "error": e}
                        )
                        continue
                    try:
                        new_discount = await new_vendor_product_class_discount(
                            token,
                            session,
                            NewVendorProductClassDiscount(data=data),
                        )
                        new_discount = VendorProductClassDiscountResourceResp(
                            **new_discount
                        )
                    except HTTPException as http_e:
                        if http_e.status_code == 409:
                            ex_id_sql = """
                                SELECT id
                                FROM vendor_product_class_discounts
                                WHERE base_price_class = :bpc
                                AND label_price_class = :lpc
                                AND product_class_id = :pcid
                                AND vendor_customer_id = :vcid
                            """
                            params = dict(
                                bpc=base_class_id,
                                lpc=label_class_id,
                                pcid=product_class_id,
                                vcid=customer_id,
                            )
                            existing_id = DB_V2.execute(
                                session, ex_id_sql, params
                            ).scalar_one()

                            mod_obj = ModVendorProductClassDiscount(
                                data=ModVendorProductClassDiscountRObj(
                                    id=existing_id,
                                    type=data.type,
                                    attributes=data.attributes,
                                    relationships=data.relationships,
                                )
                            )
                            try:
                                updated_record = (
                                    await mod_vendor_product_class_discount(
                                        token,
                                        session,
                                        existing_id,
                                        mod_obj,
                                    )
                                )
                                updated_record = VendorProductClassDiscountResourceResp(
                                    **updated_record
                                )
                            except Exception as e:
                                logger.error(f"Error updating product discount: {e}")
                                errors[record_type].append(
                                    {"record": record_.model_dump(), "error": e}
                                )
                                continue
                            else:
                                updates[record_type].append(
                                    {
                                        "record": record_.model_dump(),
                                        "id": updated_record.data.id,
                                    }
                                )
                                session.commit()
                        else:
                            raise e
                    except Exception as e:
                        logger.error(f"Error establishing product discount: {e}")
                        errors[record_type].append(
                            {"record": record_.model_dump(), "error": e}
                        )
                        continue
                    else:
                        inserts[record_type].append(
                            {"record": record_.model_dump(), "id": new_discount.data.id}
                        )
                        session.commit()

            case PriceTemplateSheet.PRODUCT_DISCOUNTS:
                record: ProductDiscountDTO
                errors.setdefault(record_type, [])
                updates.setdefault(record_type, [])
                inserts.setdefault(record_type, [])

    new_meta = dict(errors=errors, updates=updates, inserts=inserts)
    ret = await vendor_customer_pricing(
        token,
        session,
        vendor_id,
        customer_id,
        None,
        ReturnType.JSON,
    )
    ret.meta = new_meta
    return ret


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


def parse_pricing_template(data: BytesIO) -> dict[StrEnum, list[BaseModel]]:
    data.seek(0)
    wb = openpyxl.load_workbook(data, data_only=True)
    ret: dict[StrEnum, list] = {}
    try:
        sheet_names = set(wb.sheetnames)
        expected_sheets = set([sheet.value for sheet in PriceTemplateSheet])
        if extra_sheets := sheet_names - expected_sheets:
            logger.warning(f"Additional sheets present: {extra_sheets}")
        elif expected_sheets - sheet_names == expected_sheets:
            msg = "None of the expected sheets are present in the file."
            msg += " Expected at least one sheet with the following names: "
            msg += f"{', '.join(expected_sheets)}"
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=msg)
        elif missing_sheets := expected_sheets - sheet_names:
            logger.warning(f"Missing Sheets: {missing_sheets}")

        for sheet_name in sheet_names:
            sheet = wb[sheet_name]
            template_sheet_enum = PriceTemplateSheet(sheet_name)
            expected_columns = set(PriceTemplateSheetColumns[template_sheet_enum])
            visited = set()
            for cell in sheet[1]:
                if cell.value not in expected_columns:
                    msg = f"Unexpected column: {cell.value}"
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, msg)
                else:
                    visited.add(cell.value)
            if missing := expected_columns - visited:
                msg = f"Expected columns for sheet {sheet_name} are missing: {missing}"
                raise HTTPException(status.HTTP_400_BAD_REQUEST, msg)
            first_row = [cell.value for cell in sheet[2]]
            missing_or_incomplete_first_row = not any(first_row) or not all(first_row)
            if missing_or_incomplete_first_row:
                logger.warning(f"Skipping {sheet_name}")
                continue
            else:
                data_model = PriceTemplateModels[template_sheet_enum]
                for row in sheet.iter_rows(min_row=2):
                    row_vals = (cell.value for cell in row)
                    incomplete_row = not any(row_vals) or not all(row_vals)
                    if incomplete_row:
                        continue
                    data_obj = {
                        k: v
                        for k, v in zip(
                            data_model.model_fields.keys(), (cell.value for cell in row)
                        )
                    }
                    ret.setdefault(template_sheet_enum, list())
                    ret[template_sheet_enum].append(data_model(**data_obj))
    except Exception as e:
        raise e
    else:
        ret = {k: v for k, v in ret.items() if v}
        if ret:
            return ret
        msg = "Pricing Update file is empty"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, msg)
    finally:
        wb.close()
        data.seek(0)
