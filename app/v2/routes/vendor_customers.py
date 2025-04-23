from typing import Annotated
from logging import getLogger
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.db.sql import queries
from app.v2.models import (
    VendorCustomerResourceResp,
    ModVendorCustomer,
    NewVendorCustomer,
)
from app.jsonapi.sqla_models import VendorCustomer

PARENT_PREFIX = "/vendors"
VENDOR_CUSTOMERS = VendorCustomer.__jsonapi_type_override__

vendor_customers = APIRouter(prefix=f"/{VENDOR_CUSTOMERS}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]

logger = getLogger("uvicorn.info")


@vendor_customers.post(
    "",
    response_model=VendorCustomerResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_customer(
    token: Token,
    session: NewSession,
    new_obj: NewVendorCustomer,
) -> VendorCustomerResourceResp:
    vendor_id = new_obj.data.relationships.vendors.data[0].id
    custom_attributes = new_obj.data.attributes.vendor_customer_attrs
    try:
        ret = (
            auth.VendorCustomerOperations(
                token, VendorCustomer, PARENT_PREFIX, id=vendor_id
            )
            .allow_admin()
            .allow_sca()
            .allow_dev()
            .post(
                session=session,
                data=new_obj.model_dump(exclude_none=True, by_alias=True),
                primary_id=vendor_id,
            )
        )
    except Exception as e:
        raise e
    else:
        new_id = ret["data"]["id"]
        params = []
        if custom_attributes:
            logger.info("new customer added - registering custom_attributes")
            for attr in custom_attributes:
                attr_dict = attr.model_dump(exclude_none=True)
                match attr_dict:
                    case {"attr": a, "type": b, "value": c}:
                        logger.info(f"Adding attribute: {attr}, Value: {c}({b})")
                        params.append(attr_dict | {"vendor_customer_id": new_id})
                    case _:
                        logger.warning(
                            "Ignored custom attribute due to mismatch"
                            f"between obj structure and expected structure. Got: {attr_dict}"
                        )
            try:
                DB_V2.execute(session, queries.insert_vendor_customer_attrs, params)
            except Exception as e:
                logger.error(e)
                session.rollback()
            else:
                session.commit()
            finally:
                return ret
        logger.info(f"No custom attributes provided")
        return ret


@vendor_customers.patch(
    "/{vendor_customer_id}",
    response_model=VendorCustomerResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_customer(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    mod_data: ModVendorCustomer,
) -> VendorCustomerResourceResp:
    vendor_id = mod_data.data.relationships.vendors.data[0].id
    return (
        auth.VendorCustomerOperations(
            token, VendorCustomer, PARENT_PREFIX, id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_customer_id,
            primary_id=vendor_id,
        )
    )


@vendor_customers.delete(
    "/{vendor_customer_id}",
    tags=["jsonapi"],
)
async def del_vendor_customer(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorCustomerOperations(
            token, VendorCustomer, PARENT_PREFIX, id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(session, obj_id=vendor_customer_id, primary_id=vendor_id)
    )


## NOT IMPLEMENTED ##


@vendor_customers.get("", tags=["Not Implemented"])
async def vendor_customer_collection(
    token: Token, session: NewSession
) -> VendorCustomerResourceResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get("/{vendor_customer_id}", tags=["Not Implemented"])
async def vendor_customer_resource(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> VendorCustomerResourceResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get("/{vendor_customer_id}/vendors", tags=["Not Implemented"])
async def vendor_customer_related_vendors(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendors", tags=["Not Implemented"]
)
async def vendor_customer_relationships_vendors(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/vendor-pricing-by-customer",
    tags=["Not Implemented"],
)
async def vendor_customer_related_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-pricing-by-customer",
    tags=["Not Implemented"],
)
async def vendor_customer_relationships_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/vendor-customer-pricing-classes-changelog",
    tags=["Not Implemented"],
)
async def vendor_customer_related_vendor_customer_pricing_classes_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-customer-pricing-classes-changelog",
    tags=["Not Implemented"],
)
async def vendor_customer_relationships_vendor_customer_pricing_classes_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/vendor-customer-pricing-classes",
    tags=["Not Implemented"],
)
async def vendor_customer_related_vendor_customer_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-customer-pricing-classes",
    tags=["Not Implemented"],
)
async def vendor_customer_relationships_vendor_customer_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/vendor-customer-changelog",
    tags=["Not Implemented"],
)
async def vendor_customer_related_vendor_customer_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-customer-changelog",
    tags=["Not Implemented"],
)
async def vendor_customer_relationships_vendor_customer_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/vendor-quotes",
    tags=["Not Implemented"],
)
async def vendor_customer_related_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-quotes",
    tags=["Not Implemented"],
)
async def vendor_customer_relationships_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/vendor-customer-attrs",
    tags=["Not Implemented"],
)
async def vendor_customer_related_vendor_customer_attrs(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-customer-attrs",
    tags=["Not Implemented"],
)
async def vendor_customer_relationships_vendor_customer_attrs(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/vendor-product-class-discounts",
    tags=["Not Implemented"],
)
async def vendor_customer_related_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/relationships/vendor-product-class-discounts",
    tags=["Not Implemented"],
)
async def vendor_customer_relationships_vendor_product_class_discounts(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/customer-location-mapping",
    tags=["Not Implemented"],
)
async def vendor_customer_related_customer_location_mapping(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_customers.get(
    "/{vendor_customer_id}/relationships/customer-location-mapping",
    tags=["Not Implemented"],
)
async def vendor_customer_relationships_customer_location_mapping(
    token: Token,
    session: NewSession,
    vendor_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
