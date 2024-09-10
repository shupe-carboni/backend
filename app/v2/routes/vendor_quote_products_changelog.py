
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorQuoteProductChangelogResp,
    VendorQuoteProductChangelogQuery,
    VendorQuoteProductChangelogQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorQuoteProductChangelog

PARENT_PREFIX = "/vendors/v2"
VENDOR_QUOTE_PRODUCTS_CHANGELOG = VendorQuoteProductChangelog.__jsonapi_type_override__

vendor_quote_products_changelog = APIRouter(
    prefix=f"/{VENDOR_QUOTE_PRODUCTS_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorQuoteProductChangelogQueryJSONAPI)


@vendor_quote_products_changelog.get(
    "",
    response_model=VendorQuoteProductChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_products_changelog_collection(
    token: Token, session: NewSession, query: VendorQuoteProductChangelogQuery = Depends()
) -> VendorQuoteProductChangelogResp:
    return (
        auth.VOperations(token, VendorQuoteProductChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_quote_products_changelog.get(
    "/{vendor_quote_products_changelog_id}",
    response_model=VendorQuoteProductChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_products_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_quote_products_changelog_id: int,
    query: VendorQuoteProductChangelogQuery = Depends(),
) -> VendorQuoteProductChangelogResp:
    return (
        auth.VOperations(token, VendorQuoteProductChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_products_changelog_id)
    )


@vendor_quote_products_changelog.get(
    "/{vendor_quote_products_changelog_id}/vendor-quote-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_products_changelog_related_vendor_quote_products(
    token: Token,
    session: NewSession,
    vendor_quote_products_changelog_id: int,
    query: VendorQuoteProductChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuoteProductChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_products_changelog_id, "vendor-quote-products")
    )

@vendor_quote_products_changelog.get(
    "/{vendor_quote_products_changelog_id}/relationships/vendor-quote-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_products_changelog_relationships_vendor_quote_products(
    token: Token,
    session: NewSession,
    vendor_quote_products_changelog_id: int,
    query: VendorQuoteProductChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuoteProductChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_products_changelog_id, "vendor-quote-products", True)
    )

    
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
    return (
        auth.VOperations(token, VendorQuoteProductChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_quote_products_changelog_id, primary_id=vendor_quote_product_id)
    )
    