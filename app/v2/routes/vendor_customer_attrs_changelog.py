
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorCustomerAttrChangelogResp,
    VendorCustomerAttrChangelogQuery,
    VendorCustomerAttrChangelogQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorCustomerAttrChangelog

PARENT_PREFIX = "/vendors/v2"
VENDOR_CUSTOMER_ATTRS_CHANGELOG = VendorCustomerAttrChangelog.__jsonapi_type_override__

vendor_customer_attrs_changelog = APIRouter(
    prefix=f"/{VENDOR_CUSTOMER_ATTRS_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorCustomerAttrChangelogQueryJSONAPI)


@vendor_customer_attrs_changelog.get(
    "",
    response_model=VendorCustomerAttrChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_attrs_changelog_collection(
    token: Token, session: NewSession, query: VendorCustomerAttrChangelogQuery = Depends()
) -> VendorCustomerAttrChangelogResp:
    return (
        auth.VOperations(token, VendorCustomerAttrChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_customer_attrs_changelog.get(
    "/{vendor_customer_attrs_changelog_id}",
    response_model=VendorCustomerAttrChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_attrs_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_customer_attrs_changelog_id: int,
    query: VendorCustomerAttrChangelogQuery = Depends(),
) -> VendorCustomerAttrChangelogResp:
    return (
        auth.VOperations(token, VendorCustomerAttrChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_attrs_changelog_id)
    )


@vendor_customer_attrs_changelog.get(
    "/{vendor_customer_attrs_changelog_id}/vendor-customer-attrs",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_attrs_changelog_related_vendor_customer_attrs(
    token: Token,
    session: NewSession,
    vendor_customer_attrs_changelog_id: int,
    query: VendorCustomerAttrChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomerAttrChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_attrs_changelog_id, "vendor-customer-attrs")
    )

@vendor_customer_attrs_changelog.get(
    "/{vendor_customer_attrs_changelog_id}/relationships/vendor-customer-attrs",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_attrs_changelog_relationships_vendor_customer_attrs(
    token: Token,
    session: NewSession,
    vendor_customer_attrs_changelog_id: int,
    query: VendorCustomerAttrChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomerAttrChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_attrs_changelog_id, "vendor-customer-attrs", True)
    )

    
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
    return (
        auth.VOperations(token, VendorCustomerAttrChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_customer_attrs_changelog_id, primary_id=vendor_customer_attr_id)
    )
    