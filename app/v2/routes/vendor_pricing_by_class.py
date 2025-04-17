from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorPricingByClassResp,
    ModVendorPricingByClass,
    NewVendorPricingByClass,
)
from app.jsonapi.sqla_models import VendorPricingByClass

PARENT_PREFIX = "/vendors"
VENDOR_PRICING_BY_CLASS = VendorPricingByClass.__jsonapi_type_override__

vendor_pricing_by_class = APIRouter(prefix=f"/{VENDOR_PRICING_BY_CLASS}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_pricing_by_class.post(
    "",
    response_model=VendorPricingByClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    new_obj: NewVendorPricingByClass,
) -> VendorPricingByClassResp:
    vendor_pricing_class_id = (
        new_obj.data.relationships.vendor_pricing_classes.data.pop().id
    )
    vendor_id = new_obj.data.relationships.vendors.data.pop().id
    return (
        auth.VendorPricingClassOperations(
            token, VendorPricingByClass, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session=session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=vendor_pricing_class_id,
        )
    )


@vendor_pricing_by_class.patch(
    "/{vendor_pricing_by_class_id}",
    response_model=VendorPricingByClassResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_id: int,
    mod_data: ModVendorPricingByClass,
) -> VendorPricingByClassResp:
    vendor_pricing_class_id = (
        mod_data.data.relationships.vendor_pricing_classes.data.pop().id
    )
    vendor_id = mod_data.data.relationships.vendors.data.pop().id
    return (
        auth.VendorPricingClassOperations(
            token, VendorPricingByClass, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_pricing_by_class_id,
            primary_id=vendor_pricing_class_id,
        )
    )


@vendor_pricing_by_class.delete(
    "/{vendor_pricing_by_class_id}",
    tags=["jsonapi"],
)
async def del_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_id: int,
    vendor_pricing_class_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorPricingClassOperations(
            token, VendorPricingByClass, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session,
            obj_id=vendor_pricing_by_class_id,
            primary_id=vendor_pricing_class_id,
        )
    )


## NOT IMPLEMENTED ##


@vendor_pricing_by_class.get(
    "",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_collection(
    token: Token, session: NewSession
) -> VendorPricingByClassResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_class_id}",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_resource(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_id: int,
) -> VendorPricingByClassResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_class_id}/vendor-pricing-classes",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_related_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_class_id}/relationships/vendor-pricing-classes",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_relationships_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_class_id}/vendor-products",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_class_id}/relationships/vendor-products",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_class_id}/vendor-pricing-by-class-changelog",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_related_vendor_pricing_by_class_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_class_id}/relationships/vendor-pricing-by-class-changelog",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_relationships_vendor_pricing_by_class_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_class_id}/customer-pricing-by-class",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_related_customer_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_class.get(
    "/{vendor_pricing_by_class_id}/relationships/customer-pricing-by-class",
    tags=["Not Implemented"],
)
async def vendor_pricing_by_class_relationships_customer_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_by_class_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
