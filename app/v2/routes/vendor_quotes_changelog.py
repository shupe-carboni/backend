
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorQuoteChangelogResp,
    VendorQuoteChangelogQuery,
    VendorQuoteChangelogQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorQuoteChangelog

PARENT_PREFIX = "/vendors/v2"
VENDOR_QUOTES_CHANGELOG = VendorQuoteChangelog.__jsonapi_type_override__

vendor_quotes_changelog = APIRouter(
    prefix=f"/{VENDOR_QUOTES_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorQuoteChangelogQueryJSONAPI)


@vendor_quotes_changelog.get(
    "",
    response_model=VendorQuoteChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quotes_changelog_collection(
    token: Token, session: NewSession, query: VendorQuoteChangelogQuery = Depends()
) -> VendorQuoteChangelogResp:
    return (
        auth.VOperations(token, VendorQuoteChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_quotes_changelog.get(
    "/{vendor_quotes_changelog_id}",
    response_model=VendorQuoteChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quotes_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_quotes_changelog_id: int,
    query: VendorQuoteChangelogQuery = Depends(),
) -> VendorQuoteChangelogResp:
    return (
        auth.VOperations(token, VendorQuoteChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quotes_changelog_id)
    )


@vendor_quotes_changelog.get(
    "/{vendor_quotes_changelog_id}/vendor-quotes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quotes_changelog_related_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_quotes_changelog_id: int,
    query: VendorQuoteChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuoteChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quotes_changelog_id, "vendor-quotes")
    )

@vendor_quotes_changelog.get(
    "/{vendor_quotes_changelog_id}/relationships/vendor-quotes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quotes_changelog_relationships_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_quotes_changelog_id: int,
    query: VendorQuoteChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuoteChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quotes_changelog_id, "vendor-quotes", True)
    )

    
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
    return (
        auth.VOperations(token, VendorQuoteChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_quotes_changelog_id, primary_id=vendor_quote_id)
    )
    