import logging
from datetime import datetime, date
from typing import Annotated
from fastapi import (
    HTTPException,
    Depends,
    UploadFile,
    status,
    Response,
    BackgroundTasks,
)
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app import auth
from app.db import DB_V2
from numpy import nan
from pandas import read_csv, ExcelFile
from app.admin.models import VendorId
from app.admin.price_updates.price_update_handlers import (
    atco_price_update,
    adp_price_update,
    apply_percentage,
    friedrich_price_update,
)
from app.db.sql import queries
from app.admin.templates import templates
from app.downloads import (
    XLSXFileResponse,
    StreamingResponse,
)

price_updates = APIRouter(prefix=f"/admin/price-updates", tags=["admin"])
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]
logger = logging.getLogger("uvicorn.info")


@price_updates.post("/implement")
async def establish_current_pricing_using_future(session: NewSession, token: Token):
    """
    Check whether any of the futures tables contains any data with an effective_date
    on or before the current system date. The check query returns a mapping to booleans
    with the same keys used for the `update_queries` mapping. If the update query
    key maps to True (there are records that exist to update), the query runs.
    """
    if token.permissions < auth.Permissions.sca_admin:
        logger.info("Insufficient permissions. Rejected.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    today_date = datetime.today().date()
    check_for_updates = queries.signal_updatable_futures
    update_queries = {
        "any_class_pricing_future": queries.class_pricing_update,
        "any_customer_pricing_future": queries.customer_pricing_update,
        "any_product_class_disc_future": queries.customer_product_class_discount_update,
        "any_product_disc_future": queries.customer_product_discount_update,
        "any_product_series_future": queries.product_series_update,
        "any_product_series_overrides": queries.product_series_overrides_expired,
    }

    session.begin()
    try:
        param = dict(today_date=today_date)
        # query name to boolean mapping
        update = DB_V2.execute(session, check_for_updates, param).mappings().fetchone()
        for query in update_queries:
            if update[query]:
                DB_V2.execute(session, update_queries[query], param)
    except Exception as e:
        logger.critical(e)
        session.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.info("Prices and discounts updated")
        session.commit()
        return Response(
            status_code=status.HTTP_200_OK, content="Prices and discounts updated"
        )
    finally:
        session.close()


@price_updates.post("/{vendor_id}")
async def new_future_pricing(
    bg: BackgroundTasks,
    session: NewSession,
    token: Token,
    vendor_id: VendorId,
    effective_date: datetime,
    file: UploadFile = None,
    increase_pct: int | float = 0,
) -> None:
    """
    Establish future pricing for a bulk price adjustment potenatially across all customers

    Take files as-is, assuming only one file, and parse it for a whole-catalog
    pricing update.

    The following method is highly coupled to vendor file structure & pricing structure,
    and while used infrequently, it is designed for powerfully large updates to business
    critical price information. It may break due to small tweaks to file structure or
    unexpected pricing behavior.

    Firstly, only an SCA admin may execute this method.
    The file is read, and the data, either in the form of a CSV or an Excel file,
    will be routed to a vendor-specific method based on the vendor_id passed into the
    route.

    Good Luck.
    """
    logger.info("Price Update request recieved")
    if token.permissions < auth.Permissions.sca_admin:
        logger.info("Insufficient permissions. Rejected.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if file and increase_pct:
        detail = "Expecting either a file *or* a percentage to apply, not both."
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail=detail)
    elif file:
        logger.info("File received")
        file_data = await file.read()
        match file.content_type:
            case "text/csv":
                file_df_collection = {"csv": read_csv(file_data).replace({nan: None})}
            case "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                with ExcelFile(file_data) as excel_file:
                    file_df_collection = {
                        sheet.title.strip(): excel_file.parse(
                            sheet.title, data_only=True
                        ).replace({nan: None})
                        for sheet in excel_file.book.worksheets
                        if sheet.sheet_state == "visible"
                    }
            case _:
                raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        logger.info(f"File read sucessfully - Routing to {vendor_id}")
    elif increase_pct:
        logger.info(f"A percentage increase received: {increase_pct}")
    else:
        msg = "must supply either a file or an increase percentage"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, msg)

    match vendor_id:
        case VendorId.ATCO:
            atco_price_update(session, file_df_collection, effective_date)
        case VendorId.ADP:
            adp_price_update(session, file_df_collection, effective_date, bg)
        case VendorId.VYBOND:
            apply_percentage(
                session=session,
                vendor_id=vendor_id,
                increase_pct=increase_pct,
                effective_date=effective_date,
            )
        case VendorId.FRIEDRICH:
            friedrich_price_update(session, file_df_collection, effective_date)
        case VendorId.GLASFLOSS:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
        case VendorId.MILWAUKEE:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
        case _:
            logger.info(f"vendor {vendor_id} unable to be routed")
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)

    return Response(status_code=status.HTTP_200_OK)


@price_updates.post("/{vendor_id}/rollback")
async def rollback_an_implemented_update(
    session: NewSession,
    token: Token,
    vendor_id: VendorId,
    current_effective_date: datetime,
    new_effective_date: datetime,
):
    """If an increase/bulk-adjustment has already been implemented (current date went beyond effective
    date), this rolls back that action and sets a new effective_date.
        - Assume pricing is in effect now
            (vendor_pricing_by_class, vendor_pricing_by_customer,
            vendor_product_class_discounts, vendor_product_discounts,
            vendor_product_series_pricing)
        - Any pricing in effect now, don't assume that there is only one history record correlated to it
        - take everything that's current and with an effective_date set to current_effective_date,
                put it into future, with new_effective_date
            (vendor_pricing_by_class_future, vendor_pricing_by_customer_future,
            vendor_product_class_discounts_future, vendor_product_discounts_future,
            vendor_product_series_pricing_future)
        - joining current with history, update current with the most recently timestamped
            record with an effective date closest to the current_effective_date.
    """
    if token.permissions < auth.Permissions.sca_admin:
        logger.info("Insufficient permissions. Rejected.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    elif (
        new_effective_date < current_effective_date
        or new_effective_date < datetime.today()
    ):
        msg = (
            "Invalid dates. "
            "The new date must be after the current date supplied,"
            "and the new date must be in the future"
        )
        logger.error(msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    rollback_query = queries.rollback_price_increase
    try:
        params = dict(
            cur_eff_date=current_effective_date.date(),
            new_eff_date=new_effective_date.date(),
            vendor_id=vendor_id.value,
        )
        DB_V2.execute(session, rollback_query, params)
    except Exception as e:
        logger.critical(e)
        session.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.info(
            f"Prices and discounts rolled back to {current_effective_date.date()}."
        )
        logger.info(
            f"Prices and discounts increase set to {new_effective_date.date()}."
        )
        session.commit()
        return Response(
            status_code=status.HTTP_200_OK,
            content=f"Prices and discounts rolled back for {vendor_id}",
        )
    finally:
        session.close()


@price_updates.get(
    "/upload-template",
    response_class=StreamingResponse,
    response_model=None,
    tags=["templates", "pricing", "download"],
)
async def download_price_file_update_template() -> XLSXFileResponse:
    """Download the template file for bulk-uploading of customer pricing"""
    try:
        return XLSXFileResponse(
            content=templates.pricing_update, filename="upload-template"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@price_updates.post("/{vendor_id}/delay")
async def delay_effective_date_on_future_pricing_not_yet_implemented(
    session: NewSession,
    token: Token,
    vendor_id: VendorId,
    current_effective_date: date,
    new_effective_date: date,
):
    """Change the effective dates on all future pricing/discounts for a given vendor
    Runs updates on all *_future tables where vendor_id and effective date match.
    """

    if token.permissions < auth.Permissions.sca_admin:
        logger.info("Insufficient permissions")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    futures_update_check_by_table = queries.delay_signal_eligible_tables

    futures_update_queries = {
        "any_class_pricing_future": queries.delay_pricing_by_class,
        "any_customer_pricing_future": queries.delay_pricing_by_customer,
        "any_product_class_disc_future": queries.delay_product_class_discounts,
        "any_product_disc_future": queries.delay_product_discounts,
        "any_product_series_future": queries.delay_product_series_pricing,
    }
    futures_update_ret_names = {
        "any_class_pricing_future": "Class Pricing",
        "any_customer_pricing_future": "Customer Pricing",
        "any_product_class_disc_future": "Product Class Discounts",
        "any_product_disc_future": "Product Discounts",
        "any_product_series_future": "Product Series Pricing",
    }
    session.begin()
    try:
        update_status = {"updated": [], "not_updated": []}
        params = dict(
            vendor_id=vendor_id.value,
            curr_eff_date=current_effective_date,
            new_eff_date=new_effective_date,
        )
        to_update_map = (
            DB_V2.execute(session, futures_update_check_by_table, params)
            .mappings()
            .fetchone()
        )
        for q in futures_update_queries:
            q_ret_name = futures_update_ret_names[q]
            if to_update_map[q]:
                DB_V2.execute(session, futures_update_queries[q], params)
                update_status["updated"].append(q_ret_name)
            else:
                update_status["not_updated"].append(q_ret_name)

    except Exception as e:
        logger.critical(e)
        session.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        session.commit()
        return update_status
    finally:
        session.close()
