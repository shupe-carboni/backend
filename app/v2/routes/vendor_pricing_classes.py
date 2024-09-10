
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorPricingClassResp,
    VendorPricingClassQuery,
    VendorPricingClassQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorPricingClass

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRICING_CLASSES = VendorPricingClass.__jsonapi_type_override__

vendor_pricing_classes = APIRouter(
    prefix=f"/{VENDOR_PRICING_CLASSES}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorPricingClassQueryJSONAPI)


@vendor_pricing_classes.get(
    "",
    response_model=VendorPricingClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_classe_collection(
    token: Token, session: NewSession, query: VendorPricingClassQuery = Depends()
) -> VendorPricingClassResp:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_pricing_classes.get(
    "/{vendor_pricing_classe_id}",
    response_model=VendorPricingClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_classe_resource(
    token: Token,
    session: NewSession,
    vendor_pricing_classe_id: int,
    query: VendorPricingClassQuery = Depends(),
) -> VendorPricingClassResp:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_classe_id)
    )


@vendor_pricing_classes.get(
    "/{vendor_pricing_classe_id}/vendors",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_classe_related_vendors(
    token: Token,
    session: NewSession,
    vendor_pricing_classe_id: int,
    query: VendorPricingClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_classe_id, "vendors")
    )

@vendor_pricing_classes.get(
    "/{vendor_pricing_classe_id}/relationships/vendors",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_classe_relationships_vendors(
    token: Token,
    session: NewSession,
    vendor_pricing_classe_id: int,
    query: VendorPricingClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_classe_id, "vendors", True)
    )

    
@vendor_pricing_classes.get(
    "/{vendor_pricing_classe_id}/vendor-pricing-by-class",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_classe_related_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_classe_id: int,
    query: VendorPricingClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_classe_id, "vendor-pricing-by-class")
    )

@vendor_pricing_classes.get(
    "/{vendor_pricing_classe_id}/relationships/vendor-pricing-by-class",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_classe_relationships_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_classe_id: int,
    query: VendorPricingClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_classe_id, "vendor-pricing-by-class", True)
    )

    
@vendor_pricing_classes.get(
    "/{vendor_pricing_classe_id}/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_classe_related_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_classe_id: int,
    query: VendorPricingClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_classe_id, "vendor-pricing-by-customer")
    )

@vendor_pricing_classes.get(
    "/{vendor_pricing_classe_id}/relationships/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_classe_relationships_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_classe_id: int,
    query: VendorPricingClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_classe_id, "vendor-pricing-by-customer", True)
    )

    
@vendor_pricing_classes.get(
    "/{vendor_pricing_classe_id}/vendor-customer-pricing-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_classe_related_vendor_customer_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_pricing_classe_id: int,
    query: VendorPricingClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_classe_id, "vendor-customer-pricing-classes")
    )

@vendor_pricing_classes.get(
    "/{vendor_pricing_classe_id}/relationships/vendor-customer-pricing-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_classe_relationships_vendor_customer_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_pricing_classe_id: int,
    query: VendorPricingClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_classe_id, "vendor-customer-pricing-classes", True)
    )

    
@vendor_pricing_classes.get(
    "/{vendor_pricing_classe_id}/vendor-customer-pricing-classes-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_classe_related_vendor_customer_pricing_classes_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_classe_id: int,
    query: VendorPricingClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_classe_id, "vendor-customer-pricing-classes-changelog")
    )

@vendor_pricing_classes.get(
    "/{vendor_pricing_classe_id}/relationships/vendor-customer-pricing-classes-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_classe_relationships_vendor_customer_pricing_classes_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_classe_id: int,
    query: VendorPricingClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_classe_id, "vendor-customer-pricing-classes-changelog", True)
    )

    

from app.v2.models import ModVendorPricingClass

@vendor_pricing_classes.patch(
    "/{vendor_pricing_classe_id}",
    response_model=VendorPricingClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_pricing_classe(
    token: Token,
    session: NewSession,
    vendor_pricing_classe_id: int,
    mod_data: ModVendorPricingClass,
) -> VendorPricingClassResp:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_pricing_classe_id,
                primary_id=mod_data.data.relationships.vendors.data.id
            )
        )

        
@vendor_pricing_classes.delete(
    "/{vendor_pricing_classe_id}",
    tags=["jsonapi"],
)
async def del_vendor_pricing_classe(
    token: Token,
    session: NewSession,
    vendor_pricing_classe_id: int,
    vendor_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorPricingClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_pricing_classe_id, primary_id=vendor_id)
    )
    