from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.v2.models import (
    VendorPricingClassResourceResp,
    ModVendorPricingClass,
    NewVendorPricingClass,
)
from app.jsonapi.sqla_models import VendorPricingClass

PARENT_PREFIX = "/vendors"
VENDOR_PRICING_CLASSES = VendorPricingClass.__jsonapi_type_override__

vendor_pricing_classes = APIRouter(prefix=f"/{VENDOR_PRICING_CLASSES}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]


@vendor_pricing_classes.post(
    "",
    response_model=VendorPricingClassResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_pricing_classe(
    token: Token,
    session: NewSession,
    new_obj: NewVendorPricingClass,
) -> VendorPricingClassResourceResp:
    vendor_id = new_obj.data.relationships.vendors.data.id
    return (
        auth.VendorOperations2(token, VendorPricingClass, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session=session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=vendor_id,
        )
    )


@vendor_pricing_classes.patch(
    "/{vendor_pricing_classes_id}",
    response_model=VendorPricingClassResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_pricing_classe(
    token: Token,
    session: NewSession,
    vendor_pricing_classes_id: int,
    mod_data: ModVendorPricingClass,
) -> VendorPricingClassResourceResp:
    vendor_id = mod_data.data.relationships.vendors.data.id
    return (
        auth.VendorOperations2(token, VendorPricingClass, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_pricing_classes_id,
            primary_id=vendor_id,
        )
    )


@vendor_pricing_classes.delete("/{vendor_pricing_classes_id}", tags=["jsonapi"])
async def del_vendor_pricing_classe(
    token: Token,
    session: NewSession,
    vendor_pricing_classes_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorOperations2(token, VendorPricingClass, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(session, obj_id=vendor_pricing_classes_id, primary_id=vendor_id)
    )


## NOT IMPLEMENTED ##


@vendor_pricing_classes.get("", tags=["jsonapi"])
async def vendor_pricing_classe_collection(
    token: Token,
    session: NewSession,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_classes.get(
    "/{vendor_pricing_classes_id}",
    tags=["jsonapi"],
)
async def vendor_pricing_classe_resource(
    token: Token,
    session: NewSession,
    vendor_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_classes.get(
    "/{vendor_pricing_classes_id}/vendors",
    tags=["jsonapi"],
)
async def vendor_pricing_classe_related_vendors(
    token: Token,
    session: NewSession,
    vendor_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_classes.get(
    "/{vendor_pricing_classes_id}/relationships/vendors",
    tags=["jsonapi"],
)
async def vendor_pricing_classe_relationships_vendors(
    token: Token,
    session: NewSession,
    vendor_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_classes.get(
    "/{vendor_pricing_classes_id}/vendor-pricing-by-class",
    tags=["jsonapi"],
)
async def vendor_pricing_classe_related_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_classes.get(
    "/{vendor_pricing_classes_id}/relationships/vendor-pricing-by-class",
    tags=["jsonapi"],
)
async def vendor_pricing_classe_relationships_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_classes.get(
    "/{vendor_pricing_classes_id}/vendor-pricing-by-customer",
    tags=["jsonapi"],
)
async def vendor_pricing_classe_related_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_classes.get(
    "/{vendor_pricing_classes_id}/relationships/vendor-pricing-by-customer",
    tags=["jsonapi"],
)
async def vendor_pricing_classe_relationships_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_classes.get(
    "/{vendor_pricing_classes_id}/vendor-customer-pricing-classes",
    tags=["jsonapi"],
)
async def vendor_pricing_classe_related_vendor_customer_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_classes.get(
    "/{vendor_pricing_classes_id}/relationships/vendor-customer-pricing-classes",
    tags=["jsonapi"],
)
async def vendor_pricing_classe_relationships_vendor_customer_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_classes.get(
    "/{vendor_pricing_classes_id}/vendor-customer-pricing-classes-changelog",
    tags=["jsonapi"],
)
async def vendor_pricing_classe_related_vendor_customer_pricing_classes_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_classes.get(
    "/{vendor_pricing_classes_id}/relationships/vendor-customer-pricing-classes-changelog",
    tags=["jsonapi"],
)
async def vendor_pricing_classe_relationships_vendor_customer_pricing_classes_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
