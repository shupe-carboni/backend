
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorProductDiscountResp,
    VendorProductDiscountQuery,
    VendorProductDiscountQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorProductDiscount

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRODUCT_DISCOUNTS = VendorProductDiscount.__jsonapi_type_override__

vendor_product_discounts = APIRouter(
    prefix=f"/{VENDOR_PRODUCT_DISCOUNTS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorProductDiscountQueryJSONAPI)


@vendor_product_discounts.get(
    "",
    response_model=VendorProductDiscountResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_discount_collection(
    token: Token, session: NewSession, query: VendorProductDiscountQuery = Depends()
) -> VendorProductDiscountResp:
    return (
        auth.VOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_product_discounts.get(
    "/{vendor_product_discount_id}",
    response_model=VendorProductDiscountResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_discount_resource(
    token: Token,
    session: NewSession,
    vendor_product_discount_id: int,
    query: VendorProductDiscountQuery = Depends(),
) -> VendorProductDiscountResp:
    return (
        auth.VOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
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
        auth.VOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
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
        auth.VOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_discount_id, "vendor-products", True)
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
        auth.VOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
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
        auth.VOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_discount_id, "vendor-customers", True)
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
        auth.VOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_discount_id, "base-price-classes")
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
        auth.VOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_discount_id, "base-price-classes", True)
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
        auth.VOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_discount_id, "label-price-classes")
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
        auth.VOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_discount_id, "label-price-classes", True)
    )

    

from app.v2.models import ModVendorProductDiscount

@vendor_product_discounts.patch(
    "/{vendor_product_discount_id}",
    response_model=VendorProductDiscountResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_product_discount(
    token: Token,
    session: NewSession,
    vendor_product_discount_id: int,
    mod_data: ModVendorProductDiscount,
) -> VendorProductDiscountResp:
    return (
        auth.VOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_product_discount_id,
                primary_id=mod_data.data.relationships.vendor_customers.data.id
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
) -> None:
    return (
        auth.VOperations(token, VendorProductDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_product_discount_id, primary_id=vendor_customer_id)
    )
    