
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorCustomerPricingClassesChangelogResp,
    VendorCustomerPricingClassesChangelogQuery,
    VendorCustomerPricingClassesChangelogQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorCustomerPricingClassesChangelog

PARENT_PREFIX = "/vendors/v2"
VENDOR_CUSTOMER_PRICING_CLASSES_CHANGELOG = VendorCustomerPricingClassesChangelog.__jsonapi_type_override__

vendor_customer_pricing_classes_changelog = APIRouter(
    prefix=f"/{VENDOR_CUSTOMER_PRICING_CLASSES_CHANGELOG}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorCustomerPricingClassesChangelogQueryJSONAPI)


@vendor_customer_pricing_classes_changelog.get(
    "",
    response_model=VendorCustomerPricingClassesChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_pricing_classes_changelog_collection(
    token: Token, session: NewSession, query: VendorCustomerPricingClassesChangelogQuery = Depends()
) -> VendorCustomerPricingClassesChangelogResp:
    return (
        auth.VOperations(token, VendorCustomerPricingClassesChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_customer_pricing_classes_changelog.get(
    "/{vendor_customer_pricing_classes_changelog_id}",
    response_model=VendorCustomerPricingClassesChangelogResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_pricing_classes_changelog_resource(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_changelog_id: int,
    query: VendorCustomerPricingClassesChangelogQuery = Depends(),
) -> VendorCustomerPricingClassesChangelogResp:
    return (
        auth.VOperations(token, VendorCustomerPricingClassesChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_pricing_classes_changelog_id)
    )


@vendor_customer_pricing_classes_changelog.get(
    "/{vendor_customer_pricing_classes_changelog_id}/vendor-pricing-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_pricing_classes_changelog_related_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_changelog_id: int,
    query: VendorCustomerPricingClassesChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomerPricingClassesChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_pricing_classes_changelog_id, "vendor-pricing-classes")
    )

@vendor_customer_pricing_classes_changelog.get(
    "/{vendor_customer_pricing_classes_changelog_id}/relationships/vendor-pricing-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_pricing_classes_changelog_relationships_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_changelog_id: int,
    query: VendorCustomerPricingClassesChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomerPricingClassesChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_pricing_classes_changelog_id, "vendor-pricing-classes", True)
    )

    
@vendor_customer_pricing_classes_changelog.get(
    "/{vendor_customer_pricing_classes_changelog_id}/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_pricing_classes_changelog_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_changelog_id: int,
    query: VendorCustomerPricingClassesChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomerPricingClassesChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_pricing_classes_changelog_id, "vendor-customers")
    )

@vendor_customer_pricing_classes_changelog.get(
    "/{vendor_customer_pricing_classes_changelog_id}/relationships/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_pricing_classes_changelog_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_changelog_id: int,
    query: VendorCustomerPricingClassesChangelogQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomerPricingClassesChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_pricing_classes_changelog_id, "vendor-customers", True)
    )

    
@vendor_customer_pricing_classes_changelog.delete(
    "/{vendor_customer_pricing_classes_changelog_id}",
    tags=["jsonapi"],
)
async def del_vendor_customer_pricing_classes_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_changelog_id: int,
    vendor_customer_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorCustomerPricingClassesChangelog, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_customer_pricing_classes_changelog_id, primary_id=vendor_customer_id)
    )
    