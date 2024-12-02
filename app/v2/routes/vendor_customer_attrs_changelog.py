from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.jsonapi.sqla_models import VendorCustomerAttrChangelog

PARENT_PREFIX = "/vendors"
VENDOR_CUSTOMER_ATTRS_CHANGELOG = VendorCustomerAttrChangelog.__jsonapi_type_override__

vendor_customer_attrs_changelog = APIRouter(
    prefix=f"/{VENDOR_CUSTOMER_ATTRS_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_customer_attrs_changelog.get("", tags=["Not Implemented"])
async def vendor_customer_attrs_changelog_collection(
    token: Token,
    session: NewSession,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_attrs_changelog.get(
    "/{vendor_customer_attrs_changelog_id}", tags=["Not Implemented"]
)
async def vendor_customer_attrs_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_customer_attrs_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_attrs_changelog.get(
    "/{vendor_customer_attrs_changelog_id}/vendor-customer-attrs",
    tags=["Not Implemented"],
)
async def vendor_customer_attrs_changelog_related_vendor_customer_attrs(
    token: Token,
    session: NewSession,
    vendor_customer_attrs_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_attrs_changelog.get(
    "/{vendor_customer_attrs_changelog_id}/relationships/vendor-customer-attrs",
    tags=["Not Implemented"],
)
async def vendor_customer_attrs_changelog_relationships_vendor_customer_attrs(
    token: Token,
    session: NewSession,
    vendor_customer_attrs_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_attrs_changelog.delete(
    "/{vendor_customer_attrs_changelog_id}",
    tags=["jsonapi"],
)
async def del_vendor_customer_attrs_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_attrs_changelog_id: int,
    vendor_customer_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
