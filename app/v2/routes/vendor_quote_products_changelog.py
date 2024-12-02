from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorQuoteProductChangelogResp,
)
from app.jsonapi.sqla_models import VendorQuoteProductChangelog

PARENT_PREFIX = "/vendors"
VENDOR_QUOTE_PRODUCTS_CHANGELOG = VendorQuoteProductChangelog.__jsonapi_type_override__

vendor_quote_products_changelog = APIRouter(
    prefix=f"/{VENDOR_QUOTE_PRODUCTS_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_quote_products_changelog.get(
    "",
    tags=["jsonapi"],
)
async def vendor_quote_products_changelog_collection(
    token: Token, session: NewSession
) -> VendorQuoteProductChangelogResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quote_products_changelog.get(
    "/{vendor_quote_products_changelog_id}",
    tags=["jsonapi"],
)
async def vendor_quote_products_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_quote_products_changelog_id: int,
) -> VendorQuoteProductChangelogResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quote_products_changelog.get(
    "/{vendor_quote_products_changelog_id}/vendor-quote-products",
    tags=["jsonapi"],
)
async def vendor_quote_products_changelog_related_vendor_quote_products(
    token: Token,
    session: NewSession,
    vendor_quote_products_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quote_products_changelog.get(
    "/{vendor_quote_products_changelog_id}/relationships/vendor-quote-products",
    tags=["jsonapi"],
)
async def vendor_quote_products_changelog_relationships_vendor_quote_products(
    token: Token,
    session: NewSession,
    vendor_quote_products_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quote_products_changelog.delete(
    "/{vendor_quote_products_changelog_id}",
    tags=["jsonapi"],
)
async def del_vendor_quote_products_changelog(
    token: Token,
    session: NewSession,
    vendor_quote_products_changelog_id: int,
    vendor_quote_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
