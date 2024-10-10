from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.jsonapi.sqla_models import VendorCustomerPricingClassesChangelog

PARENT_PREFIX = "/vendors"
VENDOR_CUSTOMER_PRICING_CLASSES_CHANGELOG = (
    VendorCustomerPricingClassesChangelog.__jsonapi_type_override__
)

vendor_customer_pricing_classes_changelog = APIRouter(
    prefix=f"/{VENDOR_CUSTOMER_PRICING_CLASSES_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_customer_pricing_classes_changelog.get("", tags=["Not Implemented"])
async def vendor_customer_pricing_classes_changelog_collection(
    token: Token,
    session: NewSession,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_pricing_classes_changelog.get(
    "/{vendor_customer_pricing_classes_changelog_id}",
    tags=["Not Implemented"],
)
async def vendor_customer_pricing_classes_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_pricing_classes_changelog.get(
    "/{vendor_customer_pricing_classes_changelog_id}/vendor-pricing-classes",
    tags=["Not Implemented"],
)
async def vendor_customer_pricing_classes_changelog_related_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_pricing_classes_changelog.get(
    "/{vendor_customer_pricing_classes_changelog_id}/relationships/vendor-pricing-classes",
    tags=["Not Implemented"],
)
async def vendor_customer_pricing_classes_changelog_relationships_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_pricing_classes_changelog.get(
    "/{vendor_customer_pricing_classes_changelog_id}/vendor-customers",
    tags=["Not Implemented"],
)
async def vendor_customer_pricing_classes_changelog_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_pricing_classes_changelog.get(
    "/{vendor_customer_pricing_classes_changelog_id}/relationships/vendor-customers",
    tags=["Not Implemented"],
)
async def vendor_customer_pricing_classes_changelog_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_pricing_classes_changelog.delete(
    "/{vendor_customer_pricing_classes_changelog_id}",
    tags=["Not Implemented"],
)
async def del_vendor_customer_pricing_classes_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_changelog_id: int,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
