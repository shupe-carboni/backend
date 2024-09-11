
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorsAttrsChangelogResp,
    VendorsAttrsChangelogQuery,
    VendorsAttrsChangelogQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorsAttrsChangelog

PARENT_PREFIX = "/vendors/v2"
VENDORS_ATTRS_CHANGELOG = VendorsAttrsChangelog.__jsonapi_type_override__

vendors_attrs_changelog = APIRouter(
    prefix=f"/{VENDORS_ATTRS_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorsAttrsChangelogQueryJSONAPI)


@vendors_attrs_changelog.get(
    "",
    response_model=VendorsAttrsChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendors_attrs_changelog_collection(
    token: Token, session: NewSession, query: VendorsAttrsChangelogQuery = Depends()
) -> VendorsAttrsChangelogResp:
    return (
        auth.VOperations(token, VendorsAttrsChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendors_attrs_changelog.get(
    "/{vendors_attrs_changelog_id}",
    response_model=VendorsAttrsChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendors_attrs_changelog_resource(
    token: Token,
    session: NewSession,
    vendors_attrs_changelog_id: int,
    query: VendorsAttrsChangelogQuery = Depends(),
) -> VendorsAttrsChangelogResp:
    return (
        auth.VOperations(token, VendorsAttrsChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendors_attrs_changelog_id)
    )


@vendors_attrs_changelog.get(
    "/{vendors_attrs_changelog_id}/vendors-attrs",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendors_attrs_changelog_related_vendors_attrs(
    token: Token,
    session: NewSession,
    vendors_attrs_changelog_id: int,
    query: VendorsAttrsChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorsAttrsChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendors_attrs_changelog_id, "vendors-attrs")
    )

@vendors_attrs_changelog.get(
    "/{vendors_attrs_changelog_id}/relationships/vendors-attrs",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendors_attrs_changelog_relationships_vendors_attrs(
    token: Token,
    session: NewSession,
    vendors_attrs_changelog_id: int,
    query: VendorsAttrsChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorsAttrsChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendors_attrs_changelog_id, "vendors-attrs", True)
    )

    
@vendors_attrs_changelog.delete(
    "/{vendors_attrs_changelog_id}",
    tags=["jsonapi"],
)
async def del_vendors_attrs_changelog(
    token: Token,
    session: NewSession,
    vendors_attrs_changelog_id: int,
    vendors_attr_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorsAttrsChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendors_attrs_changelog_id, primary_id=vendors_attr_id)
    )
    