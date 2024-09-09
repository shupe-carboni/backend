
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorProductClassResp,
    VendorProductClassQuery,
    VendorProductClassQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorProductClass

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRODUCT_CLASSES = VendorProductClass.__jsonapi_type_override__

vendor_product_classes = APIRouter(
    prefix=f"/{VENDOR_PRODUCT_CLASSES}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorProductClassQueryJSONAPI)


@vendor_product_classes.get(
    "",
    response_model=VendorProductClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_classe_collection(
    token: Token, session: NewSession, query: VendorProductClassQuery = Depends()
) -> VendorProductClassResp:
    return (
        auth.VOperations(token, VendorProductClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_product_classes.get(
    "/{vendor_product_classe_id}",
    response_model=VendorProductClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_classe_resource(
    token: Token,
    session: NewSession,
    vendor_product_classe_id: int,
    query: VendorProductClassQuery = Depends(),
) -> VendorProductClassResp:
    return (
        auth.VOperations(token, VendorProductClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_classe_id)
    )


@vendor_product_classes.get(
    "/{vendor_product_classe_id}/vendors",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_classe_related_vendors(
    token: Token,
    session: NewSession,
    vendor_product_classe_id: int,
    query: VendorProductClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_classe_id, "vendors")
    )

@vendor_product_classes.get(
    "/{vendor_product_classe_id}/relationships/vendors",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_classe_relationships_vendors(
    token: Token,
    session: NewSession,
    vendor_product_classe_id: int,
    query: VendorProductClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_classe_id, "vendors", True)
    )

    
@vendor_product_classes.get(
    "/{vendor_product_classe_id}/vendor-product-to-class-mapping",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_classe_related_vendor_product_to_class_mapping(
    token: Token,
    session: NewSession,
    vendor_product_classe_id: int,
    query: VendorProductClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_classe_id, "vendor-product-to-class-mapping")
    )

@vendor_product_classes.get(
    "/{vendor_product_classe_id}/relationships/vendor-product-to-class-mapping",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_classe_relationships_vendor_product_to_class_mapping(
    token: Token,
    session: NewSession,
    vendor_product_classe_id: int,
    query: VendorProductClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_classe_id, "vendor-product-to-class-mapping", True)
    )

    
@vendor_product_classes.get(
    "/{vendor_product_classe_id}/vendor-product-class-discounts",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_classe_related_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_product_classe_id: int,
    query: VendorProductClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_classe_id, "vendor-product-class-discounts")
    )

@vendor_product_classes.get(
    "/{vendor_product_classe_id}/relationships/vendor-product-class-discounts",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_classe_relationships_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_product_classe_id: int,
    query: VendorProductClassQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_classe_id, "vendor-product-class-discounts", True)
    )

    

from app.v2.models import ModVendorProductClass

@vendor_product_classes.patch(
    "/{vendor_product_classe_id}",
    response_model=VendorProductClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_product_classe(
    token: Token,
    session: NewSession,
    vendor_product_classe_id: int,
    mod_data: ModVendorProductClass,
) -> VendorProductClassResp:
    return (
        auth.VOperations(token, VendorProductClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_product_classe_id,
                primary_id=mod_data.data.relationships.vendors.data.id
            )
        )

        
@vendor_product_classes.delete(
    "/{vendor_product_classe_id}",
    tags=["jsonapi"],
)
async def del_vendor_product_classe(
    token: Token,
    session: NewSession,
    vendor_product_classe_id: int,
    vendor_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorProductClass, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_product_classe_id, primary_id=vendor_id)
    )
    