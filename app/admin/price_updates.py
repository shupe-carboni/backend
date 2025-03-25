import logging
from datetime import datetime
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
from app.admin.price_update_handlers import atco_price_update, adp_price_update


price_updates = APIRouter(prefix=f"/admin/price-updates", tags=["admin"])
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]
logger = logging.getLogger("uvicorn.info")


@price_updates.post("/{vendor_id}")
async def new_pricing(
    bg: BackgroundTasks,
    session: NewSession,
    token: Token,
    vendor_id: VendorId,
    effective_date: datetime,
    file: UploadFile = None,
    increase_pct: int | float = 0,
) -> None:
    """Take files as-is, assuming only one file, and parse it for a whole-catalog
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
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
    elif file:
        file_data = await file.read()
        match file.content_type:
            case "text/csv":
                file_df = read_csv(file_data).replace({nan: None})
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
        # Expecting that sometimes I'll get 0.055 and sometimes I'll get 5.5
        if increase_pct > 1:
            increase_pct /= 100
        logger.info(
            f"Increase percentage of {increase_pct*100:,.2f}% "
            "will be applied to all pricing directly"
        )
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
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
        case VendorId.GLASFLOSS:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
        case VendorId.MILWAUKEE:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
        case _:
            logger.info(f"vendor {vendor_id} unable to be routed")
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return Response(status_code=status.HTTP_200_OK)


@price_updates.get("/{vendor_id}")
async def establish_current_from_current_futures(session: NewSession, token: Token):
    if token.permissions < auth.Permissions.sca_admin:
        logger.info("Insufficient permissions. Rejected.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    today_date = datetime.today().date()
    any_class = """
        SELECT id
        FROM vendor_pricing_by_class_future
        WHERE effective_date <= :today_date
        LIMIT 1;
    """
    any_customer = """
        SELECT id
        FROM vendor_pricing_by_customer_future
        WHERE effective_date <= :today_date
        LIMIT 1;
    """
    any_product_class_disc = """
        SELECT id
        FROM vendor_product_class_discounts_future
        WHERE effective_date <= :today_date
        LIMIT 1;
    """
    any_product_disc = """
        SELECT id
        FROM vendor_product_discounts_future
        WHERE effective_date <= :today_date
        LIMIT 1;
    """
    any_product_series = """
        SELECT id
        FROM vendor_product_series_pricing_future
        WHERE effective_date <= :today_date
        LIMIT 1;
    """
    class_pricing_update = """
        UPDATE vendor_pricing_by_class
        SET price = future.price, effective_date = future.effective_date
        FROM vendor_pricing_by_class_future as future
        WHERE future.price_id = vendor_pricing_by_class.id
        AND future.effective_date::DATE <= :today_date
        AND vendor_pricing_by_class.deleted_at IS NULL;

        DELETE FROM vendor_pricing_by_class_future 
        WHERE effective_date::DATE <= :today_date;
    """
    customer_pricing_update = """
        UPDATE vendor_pricing_by_customer
        SET price = future.price, effective_date = future.effective_date
        FROM vendor_pricing_by_customer_future as future
        WHERE future.price_id = vendor_pricing_by_customer.id
        AND future.effective_date::DATE <= :today_date
        AND vendor_pricing_by_customer.deleted_at IS NULL;

        DELETE FROM vendor_pricing_by_customer_future 
        WHERE effective_date::DATE <= :today_date;
    """
    customer_product_class_discount_update = """
        UPDATE vendor_product_class_discounts
        SET discount = future.discount, effective_date = future.effective_date
        FROM vendor_product_class_discounts_future as future
        WHERE future.discount_id = vendor_product_class_discounts.id
        AND future.effective_date::DATE <= :today_date
        AND vendor_product_class_discounts.deleted_at IS NULL;

        DELETE FROM vendor_product_class_discounts_future 
        WHERE effective_date::DATE <= :today_date;
    """
    customer_product_discount_update = """
        UPDATE vendor_product_discounts
        SET discount = future.discount, effective_date = future.effective_date
        FROM vendor_product_discounts_future as future
        WHERE future.discount_id = vendor_product_discounts.id
        AND future.effective_date::DATE <= :today_date
        AND vendor_product_discounts.deleted_at IS NULL;

        DELETE FROM vendor_product_discounts_future 
        WHERE effective_date::DATE <= :today_date;
    """
    product_series_update = """
        UPDATE vendor_product_series_pricing
        SET price = future.price, effective_date = future.effective_date
        FROM vendor_product_series_pricing_future as future
        WHERE future.price_id = vendor_product_series_pricing.id
        AND future.effective_date::DATE <= :today_date
        AND vendor_product_series_pricing.deleted_at IS NULL;

        DELETE FROM vendor_product_series_pricing_future 
        WHERE effective_date::DATE <= :today_date;
    """
    session.begin()
    try:
        param = dict(today_date=today_date)
        if DB_V2.execute(any_class, param).scalar_one_or_none():
            DB_V2.execute(class_pricing_update, param)
        if DB_V2.execute(any_customer, param).scalar_one_or_none():
            DB_V2.execute(customer_pricing_update, param)
        if DB_V2.execute(any_product_class_disc, param).scalar_one_or_none():
            DB_V2.execute(customer_product_class_discount_update, param)
        if DB_V2.execute(any_product_disc, param).scalar_one_or_none():
            DB_V2.execute(customer_product_discount_update, param)
        if DB_V2.execute(any_product_series, param).scalar_one_or_none():
            DB_V2.execute(product_series_update, param)
    except Exception as e:
        logger.critical(e)
        session.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.info("Prices and discounts updated")
        session.commit()
        return Response(status_code=status.HTTP_200_OK)
    finally:
        session.close()


def apply_percentage(
    session: Session,
    vendor_id: VendorId,
    increase_pct: float | int,
    effective_date: datetime,
) -> None:
    """
    Take the percentage amount and apply it to all records
    in vendor-pricing-by-customer and vendor-pricing-by-class

    Discounts are not expected to change, just the underlying price points.
    """
    class_pricing_update = """
        INSERT INTO vendor_pricing_by_class_future (price_id, price, effective_date)
        SELECT 
            class_price.id, 
            CAST(ROUND(price * :multiplier) AS INTEGER),
            :ed
        FROM vendor_pricing_by_class AS class_price
        WHERE EXISTS (
            SELECT 1
            FROM vendor_products
            WHERE vendor_products.id = class_price.product_id
            AND vendor_products.vendor_id = :vendor_id
        ) 
        AND deleted_at IS NULL;
    """
    customer_pricing_update = """
        INSERT INTO vendor_pricing_by_customer_future (price_id, price, effective_date)
        SELECT 
            customer_price.id, 
            CAST(ROUND(price * :multiplier) AS INTEGER),
            :ed
        FROM vendor_pricing_by_customer AS customer_price
        WHERE EXISTS (
            SELECT 1
            FROM vendor_products
            WHERE vendor_products.id = customer_price.product_id
            AND vendor_products.vendor_id = :vendor_id
        ) 
        AND deleted_at IS NULL;
    """
    # assume percentage is in the form like 0.055, not 5.5
    if increase_pct > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Percentage increase is over 100%: {increase_pct*100:0.2f}%",
        )
    multiplier = 1 + increase_pct
    params = dict(multiplier=multiplier, ed=effective_date, vendor_id=vendor_id.value)
    session.begin()
    try:
        DB_V2.execute(session, class_pricing_update, params)
        DB_V2.execute(session, customer_pricing_update, params)
    except Exception as e:
        logger.critical(e)
        session.rollback()
    else:
        logger.info(
            "Future Pricing established with an increase percentage of "
            f"{increase_pct*100:0.2f}%"
        )
        session.commit()
    finally:
        session.close()
