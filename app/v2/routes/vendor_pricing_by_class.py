
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorPricingByClassResp,
    VendorPricingByClassQuery,
    VendorPricingByClassQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorPricingByClass

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRICING_BY_CLASS = VendorPricingByClass.__jsonapi_type_override__

vendor_pricing_by_class = APIRouter(
    prefix=f"/{VENDOR_PRICING_BY_CLASS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorPricingByClassQueryJSONAPI)


@vendor_pricing_by_class.get(
    "",
    response_model=VendorPricingByClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_clas_collection(
    token: Token, session: NewSession, query: VendorPricingByClassQuery = Depends()
) -> VendorPricingByClassResp:
    return (
        auth.VOperations(token, VendorPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_clas_id}",
    response_model=VendorPricingByClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_clas_resource(
    token: Token,
    session: NewSession,
    vendor_pricing_by_clas_id: int,
    query: VendorPricingByClassQuery = Depends(),
) -> VendorPricingByClassResp:
    return (
        auth.VOperations(token, VendorPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_clas_id)
    )


@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_clas_id}/vendor-pricing-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_clas_related_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_pricing_by_clas_id: int,
    query: VendorPricingByClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_clas_id, "vendor-pricing-classes")
    )

@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_clas_id}/relationships/vendor-pricing-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_clas_relationships_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_pricing_by_clas_id: int,
    query: VendorPricingByClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_clas_id, "vendor-pricing-classes", True)
    )

    
@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_clas_id}/vendor-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_clas_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_pricing_by_clas_id: int,
    query: VendorPricingByClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_clas_id, "vendor-products")
    )

@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_clas_id}/relationships/vendor-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_clas_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_pricing_by_clas_id: int,
    query: VendorPricingByClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_clas_id, "vendor-products", True)
    )

    
@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_clas_id}/vendor-pricing-by-class-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_clas_related_vendor_pricing_by_class_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_by_clas_id: int,
    query: VendorPricingByClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_clas_id, "vendor-pricing-by-class-changelog")
    )

@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_clas_id}/relationships/vendor-pricing-by-class-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_clas_relationships_vendor_pricing_by_class_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_by_clas_id: int,
    query: VendorPricingByClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_clas_id, "vendor-pricing-by-class-changelog", True)
    )

    
@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_clas_id}/customer-pricing-by-class",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_clas_related_customer_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_by_clas_id: int,
    query: VendorPricingByClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_clas_id, "customer-pricing-by-class")
    )

@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_clas_id}/relationships/customer-pricing-by-class",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_clas_relationships_customer_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_by_clas_id: int,
    query: VendorPricingByClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_clas_id, "customer-pricing-by-class", True)
    )

    

from app.v2.models import ModVendorPricingByClass

@vendor_pricing_by_class.patch(
    "/{vendor_pricing_by_clas_id}",
    response_model=VendorPricingByClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_pricing_by_clas(
    token: Token,
    session: NewSession,
    vendor_pricing_by_clas_id: int,
    mod_data: ModVendorPricingByClass,
) -> VendorPricingByClassResp:
    return (
        auth.VOperations(token, VendorPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_pricing_by_clas_id,
                primary_id=mod_data.data.relationships.vendor_pricing_classes.data.id
            )
        )

        
@vendor_pricing_by_class.delete(
    "/{vendor_pricing_by_clas_id}",
    tags=["jsonapi"],
)
async def del_vendor_pricing_by_clas(
    token: Token,
    session: NewSession,
    vendor_pricing_by_clas_id: int,
    vendor_pricing_classe_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorPricingByClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_pricing_by_clas_id, primary_id=vendor_pricing_classe_id)
    )
    