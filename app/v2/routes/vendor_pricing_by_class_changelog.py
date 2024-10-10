from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorPricingByClassChangelogResp,
)
from app.jsonapi.sqla_models import VendorPricingByClassChangelog

PARENT_PREFIX = "/vendors"
VENDOR_PRICING_BY_CLASS_CHANGELOG = (
    VendorPricingByClassChangelog.__jsonapi_type_override__
)

vendor_pricing_by_class_changelog = APIRouter(
    prefix=f"/{VENDOR_PRICING_BY_CLASS_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_pricing_by_class_changelog.get(
    "",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_changelog_collection(
    token: Token,
    session: NewSession,
) -> VendorPricingByClassChangelogResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_class_changelog.get(
    "/{vendor_pricing_by_class_changelog_id}",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_changelog_id: int,
) -> VendorPricingByClassChangelogResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_class_changelog.get(
    "/{vendor_pricing_by_class_changelog_id}/vendor-pricing-by-class",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_changelog_related_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_class_changelog.get(
    "/{vendor_pricing_by_class_changelog_id}/relationships/vendor-pricing-by-class",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_changelog_relationships_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_class_changelog.delete(
    "/{vendor_pricing_by_class_changelog_id}",
    tags=["Not Implemented"],
)
async def del_vendor_pricing_by_class_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_changelog_id: int,
    vendor_pricing_by_clas_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
