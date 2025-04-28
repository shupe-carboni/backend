from datetime import datetime
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy_jsonapi.errors import ValidationError
from app import auth
from app.db import DB_V2, Session
from app.jsonapi.core_models import convert_query
from app.admin.models import VendorId
from app.admin.price_updates.price_update_handlers import recalc
from app.v2.models import (
    VendorProductDiscountCollectionResp,
    VendorProductDiscountResourceResp,
    VendorProductDiscountQuery,
    VendorProductDiscountQueryJSONAPI,
    NewVendorProductDiscount,
)
from app.jsonapi.sqla_models import VendorProductDiscount

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRODUCT_DISCOUNTS = VendorProductDiscount.__jsonapi_type_override__

ROUND_TO_DOLLAR = 100
ROUND_TO_CENT = 1

vendor_product_discounts = APIRouter(prefix=f"/{VENDOR_PRODUCT_DISCOUNTS}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]
converter = convert_query(VendorProductDiscountQueryJSONAPI)


@vendor_product_discounts.get(
    "",
    response_model=VendorProductDiscountCollectionResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_discount_collection(
    token: Token, session: NewSession, query: VendorProductDiscountQuery = Depends()
) -> VendorProductDiscountCollectionResp:
    return (
        auth.VendorCustomerOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .get(session, converter(query))
    )


@vendor_product_discounts.get(
    "/{vendor_product_discount_id}",
    response_model=VendorProductDiscountResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_discount_resource(
    token: Token,
    session: NewSession,
    vendor_product_discount_id: int,
    query: VendorProductDiscountQuery = Depends(),
) -> VendorProductDiscountResourceResp:
    return (
        auth.VendorCustomerOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .get(session, converter(query), vendor_product_discount_id)
    )


@vendor_product_discounts.get(
    "/{vendor_product_discount_id}/vendor-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_discount_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_product_discount_id: int,
    query: VendorProductDiscountQuery = Depends(),
) -> None:
    return (
        auth.VendorCustomerOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .get(session, converter(query), vendor_product_discount_id, "vendor-products")
    )


@vendor_product_discounts.get(
    "/{vendor_product_discount_id}/relationships/vendor-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_discount_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_product_discount_id: int,
    query: VendorProductDiscountQuery = Depends(),
) -> None:
    return (
        auth.VendorCustomerOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .get(
            session,
            converter(query),
            vendor_product_discount_id,
            "vendor-products",
            True,
        )
    )


@vendor_product_discounts.get(
    "/{vendor_product_discount_id}/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_discount_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_product_discount_id: int,
    query: VendorProductDiscountQuery = Depends(),
) -> None:
    return (
        auth.VendorCustomerOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .get(session, converter(query), vendor_product_discount_id, "vendor-customers")
    )


@vendor_product_discounts.get(
    "/{vendor_product_discount_id}/relationships/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_discount_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_product_discount_id: int,
    query: VendorProductDiscountQuery = Depends(),
) -> None:
    return (
        auth.VendorCustomerOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .get(
            session,
            converter(query),
            vendor_product_discount_id,
            "vendor-customers",
            True,
        )
    )


@vendor_product_discounts.get(
    "/{vendor_product_discount_id}/base-price-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_discount_related_base_price_classes(
    token: Token,
    session: NewSession,
    vendor_product_discount_id: int,
    query: VendorProductDiscountQuery = Depends(),
) -> None:
    return (
        auth.VendorCustomerOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .get(
            session, converter(query), vendor_product_discount_id, "base-price-classes"
        )
    )


@vendor_product_discounts.get(
    "/{vendor_product_discount_id}/relationships/base-price-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_discount_relationships_base_price_classes(
    token: Token,
    session: NewSession,
    vendor_product_discount_id: int,
    query: VendorProductDiscountQuery = Depends(),
) -> None:
    return (
        auth.VendorCustomerOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .get(
            session,
            converter(query),
            vendor_product_discount_id,
            "base-price-classes",
            True,
        )
    )


@vendor_product_discounts.get(
    "/{vendor_product_discount_id}/label-price-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_discount_related_label_price_classes(
    token: Token,
    session: NewSession,
    vendor_product_discount_id: int,
    query: VendorProductDiscountQuery = Depends(),
) -> None:
    return (
        auth.VendorCustomerOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .get(
            session, converter(query), vendor_product_discount_id, "label-price-classes"
        )
    )


@vendor_product_discounts.get(
    "/{vendor_product_discount_id}/relationships/label-price-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_discount_relationships_label_price_classes(
    token: Token,
    session: NewSession,
    vendor_product_discount_id: int,
    query: VendorProductDiscountQuery = Depends(),
) -> None:
    return (
        auth.VendorCustomerOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .get(
            session,
            converter(query),
            vendor_product_discount_id,
            "label-price-classes",
            True,
        )
    )


from app.v2.models import ModVendorProductDiscount


@vendor_product_discounts.post(
    "",
    response_model=VendorProductDiscountResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_product_discount(
    token: Token,
    session: NewSession,
    new_data: NewVendorProductDiscount,
) -> VendorProductDiscountResourceResp:
    vendor_id = new_data.data.relationships.vendors.data[0].id
    ref_price_class_id = new_data.data.relationships.base_price_classes.data[0].id
    new_price_class_id = new_data.data.relationships.label_price_classes.data[0].id
    effective_date = new_data.data.attributes.effective_date
    try:
        ret = (
            auth.VendorCustomerOperations(
                token, VendorProductDiscount, PARENT_PREFIX, vendor_id=vendor_id
            )
            .allow_admin()
            .allow_sca()
            .allow_dev()
            .post(
                session=session,
                data=new_data.model_dump(exclude_none=True, by_alias=True),
                primary_id=new_data.data.relationships.vendor_customers.data[0].id,
            )
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    except Exception as e:
        raise e
    else:
        recalc(
            "product",
            vendor_id,
            ref_price_class_id,
            new_price_class_id,
            effective_date,
            ret["data"]["id"],
            ret["data"]["attributes"]["deleted-at"] is not None,
        )
        return ret


@vendor_product_discounts.patch(
    "/{vendor_product_discount_id}",
    response_model=VendorProductDiscountResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_product_discount(
    token: Token,
    session: NewSession,
    vendor_product_discount_id: int,
    mod_data: ModVendorProductDiscount,
) -> VendorProductDiscountResourceResp:
    vendor_id = mod_data.data.relationships.vendors.data[0].id
    ref_price_class_id = mod_data.data.relationships.base_price_classes.data[0].id
    new_price_class_id = mod_data.data.relationships.label_price_classes.data[0].id
    effective_date = mod_data.data.attributes.effective_date
    try:
        ret = (
            auth.VendorCustomerOperations(
                token, VendorProductDiscount, PARENT_PREFIX, vendor_id=vendor_id
            )
            .allow_admin()
            .allow_sca()
            .allow_dev()
            .patch(
                session=session,
                data=mod_data.model_dump(exclude_unset=True, by_alias=True),
                obj_id=vendor_product_discount_id,
                primary_id=mod_data.data.relationships.vendor_customers.data[0].id,
            )
        )
    except Exception as e:
        raise e
    else:
        recalc(
            "product",
            vendor_id,
            ref_price_class_id,
            new_price_class_id,
            effective_date,
            ret["data"]["id"],
            ret["data"]["attributes"]["deleted-at"] is not None,
        )
        return ret


@vendor_product_discounts.delete(
    "/{vendor_product_discount_id}",
    tags=["jsonapi"],
)
async def del_vendor_product_discount(
    token: Token,
    session: NewSession,
    vendor_product_discount_id: int,
    vendor_customer_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorCustomerOperations(
            token, VendorProductDiscount, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_customer("std")
        .delete(
            session, obj_id=vendor_product_discount_id, primary_id=vendor_customer_id
        )
    )
