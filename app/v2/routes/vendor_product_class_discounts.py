
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorProductClassDiscountResp,
    VendorProductClassDiscountQuery,
    VendorProductClassDiscountQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorProductClassDiscount

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRODUCT_CLASS_DISCOUNTS = VendorProductClassDiscount.__jsonapi_type_override__

vendor_product_class_discounts = APIRouter(
    prefix=f"/{VENDOR_PRODUCT_CLASS_DISCOUNTS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorProductClassDiscountQueryJSONAPI)


@vendor_product_class_discounts.get(
    "",
    response_model=VendorProductClassDiscountResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discount_collection(
    token: Token, session: NewSession, query: VendorProductClassDiscountQuery = Depends()
) -> VendorProductClassDiscountResp:
    return (
        auth.VOperations(token, VendorProductClassDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}",
    response_model=VendorProductClassDiscountResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discount_resource(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
    query: VendorProductClassDiscountQuery = Depends(),
) -> VendorProductClassDiscountResp:
    return (
        auth.VOperations(token, VendorProductClassDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_class_discount_id)
    )


@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discount_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
    query: VendorProductClassDiscountQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClassDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_class_discount_id, "vendor-customers")
    )

@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/relationships/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discount_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
    query: VendorProductClassDiscountQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClassDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_class_discount_id, "vendor-customers", True)
    )

    
@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/vendor-product-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discount_related_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
    query: VendorProductClassDiscountQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClassDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_class_discount_id, "vendor-product-classes")
    )

@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/relationships/vendor-product-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discount_relationships_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
    query: VendorProductClassDiscountQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClassDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_class_discount_id, "vendor-product-classes", True)
    )

    
@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/vendor-product-class-discounts-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discount_related_vendor_product_class_discounts_changelog(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
    query: VendorProductClassDiscountQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClassDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_class_discount_id, "vendor-product-class-discounts-changelog")
    )

@vendor_product_class_discounts.get(
    "/{vendor_product_class_discount_id}/relationships/vendor-product-class-discounts-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discount_relationships_vendor_product_class_discounts_changelog(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
    query: VendorProductClassDiscountQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClassDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_class_discount_id, "vendor-product-class-discounts-changelog", True)
    )

    

from app.v2.models import ModVendorProductClassDiscount

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
) -> VendorProductClassDiscountResp:
    return (
        auth.VOperations(token, VendorProductClassDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_product_class_discount_id,
                primary_id=mod_data.data.relationships.vendor_customers.data.id
            )
        )

        
@vendor_product_class_discounts.delete(
    "/{vendor_product_class_discount_id}",
    tags=["jsonapi"],
)
async def del_vendor_product_class_discount(
    token: Token,
    session: NewSession,
    vendor_product_class_discount_id: int,
    vendor_customer_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorProductClassDiscount, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_product_class_discount_id, primary_id=vendor_customer_id)
    )
    