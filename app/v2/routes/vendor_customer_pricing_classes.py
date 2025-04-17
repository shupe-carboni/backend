from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.db.sql import queries
from app.v2.models import (
    VendorCustomerPricingClassResourceResp,
    NewVendorCustomerPricingClass,
    ModVendorCustomerPricingClass,
)
from app.jsonapi.sqla_models import VendorCustomerPricingClass

PARENT_PREFIX = "/vendors"
VENDOR_CUSTOMER_PRICING_CLASSES = VendorCustomerPricingClass.__jsonapi_type_override__

vendor_customer_pricing_classes = APIRouter(
    prefix=f"/{VENDOR_CUSTOMER_PRICING_CLASSES}", tags=["v2"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_customer_pricing_classes.post(
    "",
    response_model=VendorCustomerPricingClassResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_customer_pricing_classes(
    token: Token,
    session: NewSession,
    new_obj: NewVendorCustomerPricingClass,
) -> VendorCustomerPricingClassResourceResp:
    vendor_customer_id = new_obj.data.relationships.vendor_customers.data[0].id
    vendor_id = new_obj.data.relationships.vendors.data[0].id
    return (
        auth.VendorCustomerOperations(
            token, VendorCustomerPricingClass, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=vendor_customer_id,
        )
    )


@vendor_customer_pricing_classes.patch(
    "/{vendor_customer_pricing_classes_id}",
    response_model=VendorCustomerPricingClassResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_customer_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_id: int,
    mod_obj: ModVendorCustomerPricingClass,
) -> VendorCustomerPricingClassResourceResp:
    vendor_customer_id = mod_obj.data.relationships.vendor_customers.data[0].id
    vendor_id = mod_obj.data.relationships.vendors.data[0].id
    try:
        # do preflight to get pricing ids that need to have class label reassigned
        params = dict(
            vendor_id=vendor_id,
            affected_customer_pricing_class=vendor_customer_pricing_classes_id,
            customer_id=vendor_customer_id,
        )
        affected_customer_pricing_ids = (
            DB_V2.execute(
                session,
                queries.vendor_customer_pricing_class_preflight,
                params=params,
            )
            .scalars()
            .all()
        )
        ret = (
            auth.VendorCustomerOperations(
                token, VendorCustomerPricingClass, PARENT_PREFIX, vendor_id=vendor_id
            )
            .allow_admin()
            .allow_sca()
            .allow_dev()
            .patch(
                session,
                data=mod_obj.model_dump(exclude_none=True, by_alias=True),
                primary_id=vendor_customer_id,
                obj_id=vendor_customer_pricing_classes_id,
            )
        )
    except Exception as e:
        raise e
    else:
        # now change the pricing_class_id in customer_pricing where the label was used
        new_id = mod_obj.data.relationships.vendor_pricing_classes.data[0].id
        params = dict(
            new_pricing_class_id=new_id,
            affected_ids=tuple(affected_customer_pricing_ids),
        )
        DB_V2.execute(
            session, queries.vendor_customer_pricing_class_patch_followup, params=params
        )
        session.commit()
        return ret


@vendor_customer_pricing_classes.delete(
    "/{vendor_customer_pricing_classes_id}",
    tags=["jsonapi"],
)
async def del_vendor_customer_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_id: int,
    vendor_customer_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorCustomerOperations(
            token, VendorCustomerPricingClass, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session,
            obj_id=vendor_customer_pricing_classes_id,
            primary_id=vendor_customer_id,
        )
    )


## NOT IMPLEMENTED ##


@vendor_customer_pricing_classes.get("", tags=["Not Implemented"])
async def vendor_customer_pricing_classes_collection(
    token: Token,
    session: NewSession,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_pricing_classes.get(
    "/{vendor_customer_pricing_classes_id}", tags=["Not Implemented"]
)
async def vendor_customer_pricing_classes_resource(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_pricing_classes.get(
    "/{vendor_customer_pricing_classes_id}/vendor-pricing-classes",
    tags=["Not Implemented"],
)
async def vendor_customer_pricing_classes_related_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_pricing_classes.get(
    "/{vendor_customer_pricing_classes_id}/relationships/vendor-pricing-classes",
    tags=["Not Implemented"],
)
async def vendor_customer_pricing_classes_relationships_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_pricing_classes.get(
    "/{vendor_customer_pricing_classes_id}/vendor-customers", tags=["Not Implemented"]
)
async def vendor_customer_pricing_classes_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customer_pricing_classes.get(
    "/{vendor_customer_pricing_classes_id}/relationships/vendor-customers",
    tags=["Not Implemented"],
)
async def vendor_customer_pricing_classes_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_customer_pricing_classes_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
