from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import VendorProductClassDiscountsChangelogResp
from app.jsonapi.sqla_models import VendorProductClassDiscountsChangelog

PARENT_PREFIX = "/vendors"
VENDOR_PRODUCT_CLASS_DISCOUNTS_CHANGELOG = (
    VendorProductClassDiscountsChangelog.__jsonapi_type_override__
)

vendor_product_class_discounts_changelog = APIRouter(
    prefix=f"/{VENDOR_PRODUCT_CLASS_DISCOUNTS_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_product_class_discounts_changelog.get("", tags=["Not Implemented"])
async def vendor_product_class_discounts_changelog_collection(
    token: Token,
    session: NewSession,
) -> VendorProductClassDiscountsChangelogResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts_changelog.get(
    "/{vendor_product_class_discounts_changelog_id}", tags=["Not Implemented"]
)
async def vendor_product_class_discounts_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_product_class_discounts_changelog_id: int,
) -> VendorProductClassDiscountsChangelogResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts_changelog.get(
    "/{vendor_product_class_discounts_changelog_id}/vendor-product-class-discounts",
    tags=["Not Implemented"],
)
async def vendor_product_class_discounts_changelog_related_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_product_class_discounts_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts_changelog.get(
    "/{vendor_product_class_discounts_changelog_id}/relationships/vendor-product-class-discounts",
    tags=["Not Implemented"],
)
async def vendor_product_class_discounts_changelog_relationships_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_product_class_discounts_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_class_discounts_changelog.delete(
    "/{vendor_product_class_discounts_changelog_id}",
    tags=["Not Implemented"],
)
async def del_vendor_product_class_discounts_changelog(
    token: Token,
    session: NewSession,
    vendor_product_class_discounts_changelog_id: int,
    vendor_product_class_discount_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
