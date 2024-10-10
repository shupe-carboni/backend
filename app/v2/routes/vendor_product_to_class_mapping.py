from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorProductToClassMappingResp,
    ModVendorProductToClassMapping,
    NewVendorProductToClassMapping,
)
from app.jsonapi.sqla_models import VendorProductToClassMapping

PARENT_PREFIX = "/vendors"
VENDOR_PRODUCT_TO_CLASS_MAPPING = VendorProductToClassMapping.__jsonapi_type_override__

vendor_product_to_class_mapping = APIRouter(
    prefix=f"/{VENDOR_PRODUCT_TO_CLASS_MAPPING}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_product_to_class_mapping.post(
    "",
    response_model=VendorProductToClassMappingResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_product_to_class_mapping(
    token: Token,
    session: NewSession,
    new_obj: NewVendorProductToClassMapping,
) -> VendorProductToClassMappingResp:
    return (
        auth.VendorOperations2(token, VendorProductToClassMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session=session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=new_obj.data.relationships.vendor_products.data.id,
        )
    )


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
        auth.VendorOperations2(token, VendorProductToClassMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_product_to_class_mapping_id,
            primary_id=mod_data.data.relationships.vendor_products.data.id,
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
        auth.VendorOperations2(token, VendorProductToClassMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session,
            obj_id=vendor_product_to_class_mapping_id,
            primary_id=vendor_product_id,
        )
    )


## NOT IMPLEMENTED ##


@vendor_product_to_class_mapping.get("", tags=["jsonapi"])
async def vendor_product_to_class_mapping_collection(
    token: Token,
    session: NewSession,
) -> VendorProductToClassMappingResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_to_class_mapping.get(
    "/{vendor_product_to_class_mapping_id}",
    tags=["jsonapi"],
)
async def vendor_product_to_class_mapping_resource(
    token: Token,
    session: NewSession,
    vendor_product_to_class_mapping_id: int,
) -> VendorProductToClassMappingResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_to_class_mapping.get(
    "/{vendor_product_to_class_mapping_id}/vendor-product-classes",
    tags=["jsonapi"],
)
async def vendor_product_to_class_mapping_related_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_product_to_class_mapping_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_to_class_mapping.get(
    "/{vendor_product_to_class_mapping_id}/relationships/vendor-product-classes",
    tags=["jsonapi"],
)
async def vendor_product_to_class_mapping_relationships_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_product_to_class_mapping_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_to_class_mapping.get(
    "/{vendor_product_to_class_mapping_id}/vendor-products",
    tags=["jsonapi"],
)
async def vendor_product_to_class_mapping_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_product_to_class_mapping_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_to_class_mapping.get(
    "/{vendor_product_to_class_mapping_id}/relationships/vendor-products",
    tags=["jsonapi"],
)
async def vendor_product_to_class_mapping_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_product_to_class_mapping_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
