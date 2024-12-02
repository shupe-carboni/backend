from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorQuoteChangelogResp,
)
from app.jsonapi.sqla_models import VendorQuoteChangelog

PARENT_PREFIX = "/vendors"
VENDOR_QUOTES_CHANGELOG = VendorQuoteChangelog.__jsonapi_type_override__

vendor_quotes_changelog = APIRouter(
    prefix=f"/{VENDOR_QUOTES_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_quotes_changelog.get(
    "",
    tags=["jsonapi"],
)
async def vendor_quotes_changelog_collection(
    token: Token, session: NewSession
) -> VendorQuoteChangelogResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes_changelog.get(
    "/{vendor_quotes_changelog_id}",
    tags=["jsonapi"],
)
async def vendor_quotes_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_quotes_changelog_id: int,
) -> VendorQuoteChangelogResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes_changelog.get(
    "/{vendor_quotes_changelog_id}/vendor-quotes",
    tags=["jsonapi"],
)
async def vendor_quotes_changelog_related_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_quotes_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes_changelog.get(
    "/{vendor_quotes_changelog_id}/relationships/vendor-quotes",
    tags=["jsonapi"],
)
async def vendor_quotes_changelog_relationships_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_quotes_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes_changelog.delete(
    "/{vendor_quotes_changelog_id}",
    tags=["jsonapi"],
)
async def del_vendor_quotes_changelog(
    token: Token,
    session: NewSession,
    vendor_quotes_changelog_id: int,
    vendor_quote_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
