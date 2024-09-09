
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorProductToClassMappingResp,
    VendorProductToClassMappingQuery,
    VendorProductToClassMappingQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorProductToClassMapping

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRODUCT_TO_CLASS_MAPPING = VendorProductToClassMapping.__jsonapi_type_override__

vendor_product_to_class_mapping = APIRouter(
    prefix=f"/{VENDOR_PRODUCT_TO_CLASS_MAPPING}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorProductToClassMappingQueryJSONAPI)


@vendor_product_to_class_mapping.get(
    "",
    response_model=VendorProductToClassMappingResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_to_class_mapping_collection(
    token: Token, session: NewSession, query: VendorProductToClassMappingQuery = Depends()
) -> VendorProductToClassMappingResp:
    return (
        auth.VOperations(token, VendorProductToClassMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_product_to_class_mapping.get(
    "/{vendor_product_to_class_mapping_id}",
    response_model=VendorProductToClassMappingResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_to_class_mapping_resource(
    token: Token,
    session: NewSession,
    vendor_product_to_class_mapping_id: int,
    query: VendorProductToClassMappingQuery = Depends(),
) -> VendorProductToClassMappingResp:
    return (
        auth.VOperations(token, VendorProductToClassMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_to_class_mapping_id)
    )


@vendor_product_to_class_mapping.get(
    "/{vendor_product_to_class_mapping_id}/vendor-product-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_to_class_mapping_related_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_product_to_class_mapping_id: int,
    query: VendorProductToClassMappingQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductToClassMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_to_class_mapping_id, "vendor-product-classes")
    )

@vendor_product_to_class_mapping.get(
    "/{vendor_product_to_class_mapping_id}/relationships/vendor-product-classes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_to_class_mapping_relationships_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_product_to_class_mapping_id: int,
    query: VendorProductToClassMappingQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductToClassMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_to_class_mapping_id, "vendor-product-classes", True)
    )

    
@vendor_product_to_class_mapping.get(
    "/{vendor_product_to_class_mapping_id}/vendor-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_to_class_mapping_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_product_to_class_mapping_id: int,
    query: VendorProductToClassMappingQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductToClassMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_to_class_mapping_id, "vendor-products")
    )

@vendor_product_to_class_mapping.get(
    "/{vendor_product_to_class_mapping_id}/relationships/vendor-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_to_class_mapping_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_product_to_class_mapping_id: int,
    query: VendorProductToClassMappingQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductToClassMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_to_class_mapping_id, "vendor-products", True)
    )

    

from app.v2.models import ModVendorProductToClassMapping

@vendor_product_to_class_mapping.patch(
    "/{vendor_product_to_class_mapping_id}",
    response_model=VendorProductToClassMappingResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_product_to_class_mapping(
    token: Token,
    session: NewSession,
    vendor_product_to_class_mapping_id: int,
    mod_data: ModVendorProductToClassMapping,
) -> VendorProductToClassMappingResp:
    return (
        auth.VOperations(token, VendorProductToClassMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_product_to_class_mapping_id,
                primary_id=mod_data.data.relationships.vendor_products.data.id
            )
        )

        
@vendor_product_to_class_mapping.delete(
    "/{vendor_product_to_class_mapping_id}",
    tags=["jsonapi"],
)
async def del_vendor_product_to_class_mapping(
    token: Token,
    session: NewSession,
    vendor_product_to_class_mapping_id: int,
    vendor_product_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorProductToClassMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_product_to_class_mapping_id, primary_id=vendor_product_id)
    )
    