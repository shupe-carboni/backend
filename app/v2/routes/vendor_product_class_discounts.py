from logging import getLogger
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy_jsonapi.errors import ValidationError
from app import auth
from app.db import DB_V2, Session
from app.admin.models import VendorId
from app.admin.price_updates.price_update_handlers import recalc
from app.v2.models import (
    VendorProductClassDiscountResourceResp,
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
    response_model=VendorProductClassDiscountResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_product_class_discount(
    token: Token,
    session: NewSession,
    new_obj: NewVendorProductClassDiscount,
) -> VendorProductClassDiscountResourceResp:
    vendor_customer_id = new_obj.data.relationships.vendor_customers.data[0].id
    vendor_id = new_obj.data.relationships.vendors.data[0].id
    ref_price_class_id = new_obj.data.relationships.base_price_classes.data[0].id
    new_price_class_id = new_obj.data.relationships.label_price_classes.data[0].id
    product_class_id = new_obj.data.relationships.vendor_product_classes.data[0].id
    effective_date = new_obj.data.attributes.effective_date
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
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    except Exception as e:
        raise e
    else:
        new_id = ret["data"]["id"]
        deleted = ret["data"]["attributes"]["deleted-at"] is not None
        recalc(
            "product_class",
            vendor_id,
            ref_price_class_id,
            new_price_class_id,
            effective_date,
            new_id,
            deleted,
        )
        return ret


@vendor_product_class_discounts.patch(
    "/{vendor_product_class_discount_id}",
    response_model=VendorProductClassDiscountResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_product_class_discount(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
    mod_data: ModVendorProductClassDiscount,
) -> VendorProductClassDiscountResourceResp:
    vendor_customer_id = mod_data.data.relationships.vendor_customers.data[0].id
    vendor_id = mod_data.data.relationships.vendors.data[0].id
    ref_price_class_id = mod_data.data.relationships.base_price_classes.data[0].id
    new_price_class_id = mod_data.data.relationships.label_price_classes.data[0].id
    effective_date = mod_data.data.attributes.effective_date
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
        deleted = ret["data"]["attributes"]["deleted-at"] is not None
        recalc(
            "product_class",
            vendor_id,
            ref_price_class_id,
            new_price_class_id,
            effective_date,
            vendor_product_class_discount_id,
            deleted,
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
    vendor_id: VendorId,
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
) -> VendorProductClassDiscountResourceResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}",
    tags=["jsonapi"],
)
async def vendor_product_class_discount_resource(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
) -> VendorProductClassDiscountResourceResp:
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
