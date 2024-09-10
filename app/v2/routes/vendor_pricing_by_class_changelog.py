
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorPricingByClassChangelogResp,
    VendorPricingByClassChangelogQuery,
    VendorPricingByClassChangelogQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorPricingByClassChangelog

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRICING_BY_CLASS_CHANGELOG = VendorPricingByClassChangelog.__jsonapi_type_override__

vendor_pricing_by_class_changelog = APIRouter(
    prefix=f"/{VENDOR_PRICING_BY_CLASS_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorPricingByClassChangelogQueryJSONAPI)


@vendor_pricing_by_class_changelog.get(
    "",
    response_model=VendorPricingByClassChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_class_changelog_collection(
    token: Token, session: NewSession, query: VendorPricingByClassChangelogQuery = Depends()
) -> VendorPricingByClassChangelogResp:
    return (
        auth.VOperations(token, VendorPricingByClassChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_pricing_by_class_changelog.get(
    "/{vendor_pricing_by_class_changelog_id}",
    response_model=VendorPricingByClassChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_class_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_changelog_id: int,
    query: VendorPricingByClassChangelogQuery = Depends(),
) -> VendorPricingByClassChangelogResp:
    return (
        auth.VOperations(token, VendorPricingByClassChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_class_changelog_id)
    )


@vendor_pricing_by_class_changelog.get(
    "/{vendor_pricing_by_class_changelog_id}/vendor-pricing-by-class",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_class_changelog_related_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_changelog_id: int,
    query: VendorPricingByClassChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByClassChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_class_changelog_id, "vendor-pricing-by-class")
    )

@vendor_pricing_by_class_changelog.get(
    "/{vendor_pricing_by_class_changelog_id}/relationships/vendor-pricing-by-class",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_class_changelog_relationships_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_changelog_id: int,
    query: VendorPricingByClassChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByClassChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_class_changelog_id, "vendor-pricing-by-class", True)
    )

    
@vendor_pricing_by_class_changelog.delete(
    "/{vendor_pricing_by_class_changelog_id}",
    tags=["jsonapi"],
)
async def del_vendor_pricing_by_class_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_changelog_id: int,
    vendor_pricing_by_clas_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorPricingByClassChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_pricing_by_class_changelog_id, primary_id=vendor_pricing_by_clas_id)
    )
    