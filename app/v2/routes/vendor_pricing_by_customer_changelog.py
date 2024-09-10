
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorPricingByCustomerChangelogResp,
    VendorPricingByCustomerChangelogQuery,
    VendorPricingByCustomerChangelogQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorPricingByCustomerChangelog

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRICING_BY_CUSTOMER_CHANGELOG = VendorPricingByCustomerChangelog.__jsonapi_type_override__

vendor_pricing_by_customer_changelog = APIRouter(
    prefix=f"/{VENDOR_PRICING_BY_CUSTOMER_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorPricingByCustomerChangelogQueryJSONAPI)


@vendor_pricing_by_customer_changelog.get(
    "",
    response_model=VendorPricingByCustomerChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_changelog_collection(
    token: Token, session: NewSession, query: VendorPricingByCustomerChangelogQuery = Depends()
) -> VendorPricingByCustomerChangelogResp:
    return (
        auth.VOperations(token, VendorPricingByCustomerChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_pricing_by_customer_changelog.get(
    "/{vendor_pricing_by_customer_changelog_id}",
    response_model=VendorPricingByCustomerChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_changelog_id: int,
    query: VendorPricingByCustomerChangelogQuery = Depends(),
) -> VendorPricingByCustomerChangelogResp:
    return (
        auth.VOperations(token, VendorPricingByCustomerChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_changelog_id)
    )


@vendor_pricing_by_customer_changelog.get(
    "/{vendor_pricing_by_customer_changelog_id}/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_changelog_related_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_changelog_id: int,
    query: VendorPricingByCustomerChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomerChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_changelog_id, "vendor-pricing-by-customer")
    )

@vendor_pricing_by_customer_changelog.get(
    "/{vendor_pricing_by_customer_changelog_id}/relationships/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_changelog_relationships_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_changelog_id: int,
    query: VendorPricingByCustomerChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomerChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_changelog_id, "vendor-pricing-by-customer", True)
    )

    
@vendor_pricing_by_customer_changelog.delete(
    "/{vendor_pricing_by_customer_changelog_id}",
    tags=["jsonapi"],
)
async def del_vendor_pricing_by_customer_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_changelog_id: int,
    vendor_pricing_by_customer_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomerChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_pricing_by_customer_changelog_id, primary_id=vendor_pricing_by_customer_id)
    )
    