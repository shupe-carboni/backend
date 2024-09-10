
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorProductClassDiscountsChangelogResp,
    VendorProductClassDiscountsChangelogQuery,
    VendorProductClassDiscountsChangelogQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorProductClassDiscountsChangelog

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRODUCT_CLASS_DISCOUNTS_CHANGELOG = VendorProductClassDiscountsChangelog.__jsonapi_type_override__

vendor_product_class_discounts_changelog = APIRouter(
    prefix=f"/{VENDOR_PRODUCT_CLASS_DISCOUNTS_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorProductClassDiscountsChangelogQueryJSONAPI)


@vendor_product_class_discounts_changelog.get(
    "",
    response_model=VendorProductClassDiscountsChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discounts_changelog_collection(
    token: Token, session: NewSession, query: VendorProductClassDiscountsChangelogQuery = Depends()
) -> VendorProductClassDiscountsChangelogResp:
    return (
        auth.VOperations(token, VendorProductClassDiscountsChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_product_class_discounts_changelog.get(
    "/{vendor_product_class_discounts_changelog_id}",
    response_model=VendorProductClassDiscountsChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discounts_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_product_class_discounts_changelog_id: int,
    query: VendorProductClassDiscountsChangelogQuery = Depends(),
) -> VendorProductClassDiscountsChangelogResp:
    return (
        auth.VOperations(token, VendorProductClassDiscountsChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_class_discounts_changelog_id)
    )


@vendor_product_class_discounts_changelog.get(
    "/{vendor_product_class_discounts_changelog_id}/vendor-product-class-discounts",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discounts_changelog_related_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_product_class_discounts_changelog_id: int,
    query: VendorProductClassDiscountsChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClassDiscountsChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_class_discounts_changelog_id, "vendor-product-class-discounts")
    )

@vendor_product_class_discounts_changelog.get(
    "/{vendor_product_class_discounts_changelog_id}/relationships/vendor-product-class-discounts",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_class_discounts_changelog_relationships_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_product_class_discounts_changelog_id: int,
    query: VendorProductClassDiscountsChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClassDiscountsChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_class_discounts_changelog_id, "vendor-product-class-discounts", True)
    )

    
@vendor_product_class_discounts_changelog.delete(
    "/{vendor_product_class_discounts_changelog_id}",
    tags=["jsonapi"],
)
async def del_vendor_product_class_discounts_changelog(
    token: Token,
    session: NewSession,
    vendor_product_class_discounts_changelog_id: int,
    vendor_product_class_discount_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorProductClassDiscountsChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_product_class_discounts_changelog_id, primary_id=vendor_product_class_discount_id)
    )
    