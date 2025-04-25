from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.jsonapi.core_models import convert_query
from app.v2.models import (
    VendorProductDiscountCollectionResp,
    VendorProductDiscountResourceResp,
    VendorProductDiscountQuery,
    VendorProductDiscountQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorProductDiscount

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRODUCT_DISCOUNTS = VendorProductDiscount.__jsonapi_type_override__

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

## TODO make a POST endpoint


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
    return (
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
