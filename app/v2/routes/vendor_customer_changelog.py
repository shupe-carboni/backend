from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.jsonapi.sqla_models import VendorCustomerChangelog

PARENT_PREFIX = "/vendors"
VENDOR_CUSTOMER_CHANGELOG = VendorCustomerChangelog.__jsonapi_type_override__

vendor_customer_changelog = APIRouter(
    prefix=f"/{VENDOR_CUSTOMER_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_customer_changelog.get("", tags=["Not Implemented"])
async def vendor_customer_changelog_collection(
    token: Token, session: NewSession
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_changelog.get(
    "/{vendor_customer_changelog_id}", tags=["Not Implemented"]
)
async def vendor_customer_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_customer_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_changelog.get(
    "/{vendor_customer_changelog_id}/vendor-customers", tags=["Not Implemented"]
)
async def vendor_customer_changelog_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_customer_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_changelog.get(
    "/{vendor_customer_changelog_id}/relationships/vendor-customers",
    tags=["Not Implemented"],
)
async def vendor_customer_changelog_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_customer_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_changelog.delete(
    "/{vendor_customer_changelog_id}",
    tags=["Not Implemented"],
)
async def del_vendor_customer_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_changelog_id: int,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
