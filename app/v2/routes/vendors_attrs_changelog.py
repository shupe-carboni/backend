from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorsAttrsChangelogResourceResp,
)
from app.jsonapi.sqla_models import VendorsAttrsChangelog

PARENT_PREFIX = "/vendors"
VENDORS_ATTRS_CHANGELOG = VendorsAttrsChangelog.__jsonapi_type_override__

vendors_attrs_changelog = APIRouter(
    prefix=f"/{VENDORS_ATTRS_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendors_attrs_changelog.get(
    "",
    tags=["Not Implemented"],
)
async def vendors_attrs_changelog_collection(
    token: Token, session: NewSession
) -> VendorsAttrsChangelogResourceResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendors_attrs_changelog.get(
    "/{vendors_attrs_changelog_id}",
    tags=["Not Implemented"],
)
async def vendors_attrs_changelog_resource(
    token: Token,
    session: NewSession,
    vendors_attrs_changelog_id: int,
) -> VendorsAttrsChangelogResourceResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendors_attrs_changelog.get(
    "/{vendors_attrs_changelog_id}/vendors-attrs",
    tags=["Not Implemented"],
)
async def vendors_attrs_changelog_related_vendors_attrs(
    token: Token,
    session: NewSession,
    vendors_attrs_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendors_attrs_changelog.get(
    "/{vendors_attrs_changelog_id}/relationships/vendors-attrs",
    tags=["Not Implemented"],
)
async def vendors_attrs_changelog_relationships_vendors_attrs(
    token: Token,
    session: NewSession,
    vendors_attrs_changelog_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendors_attrs_changelog.delete(
    "/{vendors_attrs_changelog_id}",
    tags=["Not Implemented"],
)
async def del_vendors_attrs_changelog(
    token: Token,
    session: NewSession,
    vendors_attrs_changelog_id: int,
    vendors_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
