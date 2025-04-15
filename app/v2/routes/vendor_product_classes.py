from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorProductClassResourceResp,
    ModVendorProductClass,
    NewVendorProductClass,
)
from app.jsonapi.sqla_models import VendorProductClass

PARENT_PREFIX = "/vendors"
VENDOR_PRODUCT_CLASSES = VendorProductClass.__jsonapi_type_override__

vendor_product_classes = APIRouter(prefix=f"/{VENDOR_PRODUCT_CLASSES}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_product_classes.post(
    "",
    response_model=VendorProductClassResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_product_classes(
    token: Token,
    session: NewSession,
    new_obj: NewVendorProductClass,
) -> VendorProductClassResourceResp:
    vendor_id = new_obj.data.relationships.vendors.data.id
    return (
        auth.VendorOperations2(token, VendorProductClass, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session=session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=vendor_id,
        )
    )


@vendor_product_classes.patch(
    "/{vendor_product_classes_id}",
    response_model=VendorProductClassResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_product_classes_id: int,
    mod_data: ModVendorProductClass,
) -> VendorProductClassResourceResp:
    vendor_id = mod_data.data.relationships.vendors.data.id
    return (
        auth.VendorOperations2(token, VendorProductClass, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_product_classes_id,
            primary_id=vendor_id,
        )
    )


@vendor_product_classes.delete(
    "/{vendor_product_classes_id}",
    tags=["jsonapi"],
)
async def del_vendor_product_classes(
    token: Token,
    session: NewSession,
    vendor_product_classes_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorOperations2(token, VendorProductClass, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(session, obj_id=vendor_product_classes_id, primary_id=vendor_id)
    )


@vendor_product_classes.get("", tags=["Not Implemented"])
async def vendor_product_classes_collection(
    token: Token, session: NewSession
) -> VendorProductClassResourceResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_classes.get("/{vendor_product_classes_id}", tags=["Not Implemented"])
async def vendor_product_classes_resource(
    token: Token,
    session: NewSession,
    vendor_product_classes_id: int,
) -> VendorProductClassResourceResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_classes.get(
    "/{vendor_product_classes_id}/vendors", tags=["Not Implemented"]
)
async def vendor_product_classes_related_vendors(
    token: Token,
    session: NewSession,
    vendor_product_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_classes.get(
    "/{vendor_product_classes_id}/relationships/vendors", tags=["Not Implemented"]
)
async def vendor_product_classes_relationships_vendors(
    token: Token,
    session: NewSession,
    vendor_product_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_classes.get(
    "/{vendor_product_classes_id}/vendor-product-to-class-mapping",
    tags=["Not Implemented"],
)
async def vendor_product_classes_related_vendor_product_to_class_mapping(
    token: Token,
    session: NewSession,
    vendor_product_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_classes.get(
    "/{vendor_product_classes_id}/relationships/vendor-product-to-class-mapping",
    tags=["Not Implemented"],
)
async def vendor_product_classes_relationships_vendor_product_to_class_mapping(
    token: Token,
    session: NewSession,
    vendor_product_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_classes.get(
    "/{vendor_product_classes_id}/vendor-product-class-discounts",
    tags=["Not Implemented"],
)
async def vendor_product_classes_related_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_product_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_product_classes.get(
    "/{vendor_product_classes_id}/relationships/vendor-product-class-discounts",
    tags=["Not Implemented"],
)
async def vendor_product_classes_relationships_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_product_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
