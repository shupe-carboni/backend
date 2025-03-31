from logging import getLogger
from typing import Annotated
from fastapi import Depends, HTTPException, status, BackgroundTasks
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.db.sql import queries
from app.v2.models import (
    VendorProductClassDiscountResp,
    ModVendorProductClassDiscount,
    NewVendorProductClassDiscount,
)
from app.jsonapi.sqla_models import VendorProductClassDiscount

PARENT_PREFIX = "/vendors"
VENDOR_PRODUCT_CLASS_DISCOUNTS = VendorProductClassDiscount.__jsonapi_type_override__

ROUND_TO_DOLLAR = 100
ROUND_TO_CENT = 1

vendor_product_class_discounts = APIRouter(
    prefix=f"/{VENDOR_PRODUCT_CLASS_DISCOUNTS}", tags=["v2"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]

logger = getLogger("uvicorn.info")


@vendor_product_class_discounts.post(
    "",
    response_model=VendorProductClassDiscountResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_product_class_discount(
    token: Token,
    session: NewSession,
    new_obj: NewVendorProductClassDiscount,
    bg: BackgroundTasks,
) -> VendorProductClassDiscountResp:
    vendor_customer_id = new_obj.data.relationships.vendor_customers.data.id
    vendor_id = new_obj.data.relationships.vendors.data.id
    ref_price_class_id = new_obj.data.relationships.vendor_pricing_classes_ref.data.id
    new_price_class_id = new_obj.data.relationships.vendor_pricing_classes_new.data.id
    product_class_id = new_obj.data.relationships.vendor_product_classes.data.id
    if not product_class_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="product_class_id required"
        )
    try:
        ret = (
            auth.VendorCustomerOperations(
                token, VendorProductClassDiscount, PARENT_PREFIX, vendor_id=vendor_id
            )
            .allow_admin()
            .allow_sca()
            .allow_dev()
            .post(
                session=session,
                data=new_obj.model_dump(exclude_none=True, by_alias=True),
                primary_id=vendor_customer_id,
            )
        )
    except Exception as e:
        raise e
    else:
        match vendor_id:
            case "adp":
                sig = ROUND_TO_DOLLAR
                update_only = True
            case _:
                sig = ROUND_TO_CENT
                update_only = False
        new_id = ret["data"]["id"]
        if ret["data"]["attributes"]["deleted-at"] is None:
            bg.add_task(
                calc_customer_pricing_from_product_class_discount,
                session,
                new_id,
                ref_price_class_id,
                new_price_class_id,
                sig,
                update_only,
            )
        return ret


@vendor_product_class_discounts.patch(
    "/{vendor_product_class_discount_id}",
    response_model=VendorProductClassDiscountResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_product_class_discount(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
    mod_data: ModVendorProductClassDiscount,
    bg: BackgroundTasks,
) -> VendorProductClassDiscountResp:
    vendor_customer_id = mod_data.data.relationships.vendor_customers.data.id
    vendor_id = mod_data.data.relationships.vendors.data.id
    ref_price_class_id = mod_data.data.relationships.vendor_pricing_classes_ref.data.id
    new_price_class_id = mod_data.data.relationships.vendor_pricing_classes_new.data.id
    try:
        ret = (
            auth.VendorCustomerOperations(
                token, VendorProductClassDiscount, PARENT_PREFIX, vendor_id=vendor_id
            )
            .allow_admin()
            .allow_sca()
            .allow_dev()
            .patch(
                session=session,
                data=mod_data.model_dump(exclude_none=True, by_alias=True),
                obj_id=vendor_product_class_discount_id,
                primary_id=vendor_customer_id,
            )
        )
    except Exception as e:
        raise e
    else:
        match vendor_id:
            case "adp":
                sig = ROUND_TO_DOLLAR
                update_only = True
            case _:
                sig = ROUND_TO_CENT
                update_only = False
        if ret["data"]["attributes"]["deleted-at"] is None:
            bg.add_task(
                calc_customer_pricing_from_product_class_discount,
                session,
                vendor_product_class_discount_id,
                ref_price_class_id,
                new_price_class_id,
                sig,
                update_only,
            )
        return ret


@vendor_product_class_discounts.delete(
    "/{vendor_product_class_discount_id}",
    tags=["jsonapi"],
)
async def del_vendor_product_class_discount(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
    vendor_customer_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorCustomerOperations(
            token, VendorProductClassDiscount, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session,
            obj_id=vendor_product_class_discount_id,
            primary_id=vendor_customer_id,
        )
    )


@vendor_product_class_discounts.get("", tags=["jsonapi"])
async def vendor_product_class_discount_collection(
    token: Token,
    session: NewSession,
) -> VendorProductClassDiscountResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_resource(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> VendorProductClassDiscountResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/vendor-customers",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/relationships/vendor-customers",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/vendor-product-classes",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_related_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/relationships/vendor-product-classes",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_relationships_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/vendor-product-class-discounts-changelog",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_related_vendor_product_class_discounts_changelog(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/relationships/vendor-product-class-discounts-changelog",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_relationships_vendor_product_class_discounts_changelog(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


def calc_customer_pricing_from_product_class_discount(
    session: Session,
    product_class_discount_id: int,
    ref_pricing_class_id: int,
    new_pricing_class_id: int,
    rounding_strategy: int,
    update_only: bool = False,
) -> None:
    """
    When a customer's product-class-based pricing discount is changed, pricing reflected
    in vendor_pricing_by_customer ought to be changed as well.

    The reference pricing class id is used to identify the pricing in pricing_by_class
    that can be used as the reference price against which to apply the new multiplier.
    Rounding strategy is passed to the SQL statment to shift the truncation introduced
    by ROUND, such that we can dynamically round to the nearest dollar or the nearest
    cent.
    """
    logger.info(f"Calculating pricing related to the modified product class discount")

    update_customer_pricing = (
        queries.update_customer_pricing_after_product_class_disc_modified
    )
    add_new_customer_pricing = queries.new_customer_pricing_after_product_class_discs
    update_params = dict(
        pricing_class_id=ref_pricing_class_id,
        product_class_discount_id=product_class_discount_id,
        sig=rounding_strategy,
    )
    new_record_params = dict(
        ref_pricing_class_id=ref_pricing_class_id,
        new_price_class_id=new_pricing_class_id,
        product_class_discount_id=product_class_discount_id,
        sig=rounding_strategy,
    )
    try:
        DB_V2.execute(session, sql=update_customer_pricing, params=update_params)
        if not update_only:
            DB_V2.execute(
                session, sql=add_new_customer_pricing, params=new_record_params
            )
    except Exception as e:
        logger.critical(e)
        session.rollback()
    else:
        logger.info("Update successful")
        session.commit()
    return
