from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorPricingByCustomerResourceResp,
    ModVendorPricingByCustomer,
    NewVendorPricingByCustomer,
)
from app.jsonapi.sqla_models import VendorPricingByCustomer
from sqlalchemy_jsonapi.errors import ValidationError

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRICING_BY_CUSTOMER = VendorPricingByCustomer.__jsonapi_type_override__

vendor_pricing_by_customer = APIRouter(
    prefix=f"/{VENDOR_PRICING_BY_CUSTOMER}", tags=["v2"]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_pricing_by_customer.post(
    "",
    response_model=VendorPricingByCustomerResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    new_obj: NewVendorPricingByCustomer,
) -> VendorPricingByCustomerResourceResp:
    vendor_customer_id = new_obj.data.relationships.vendor_customers.data.pop().id
    vendor_id = new_obj.data.relationships.vendors.data.pop().id
    try:
        return (
            auth.VendorCustomerOperations(
                token, VendorPricingByCustomer, PARENT_PREFIX, vendor_id=vendor_id
            )
            .allow_admin()
            .allow_sca()
            .allow_dev()
            .post(
                session=session,
                data=new_obj.model_dump(exclude_none=True, by_alias=True),
                primary_id=vendor_customer_id,
            )
        )
    except ValidationError:
        product_id = new_obj.data.relationships.vendor_products.data.pop().id
        pricing_class_id = (
            new_obj.data.relationships.vendor_pricing_classes.data.pop().id
        )
        new_price = new_obj.data.attributes.price
        sql = """
            SELECT id
            FROM vendor_pricing_by_customer
            WHERE vendor_customer_id = :vc_id
            AND product_id = :p_id
            AND pricing_class_id = :pc_id;
        """
        (existing_id,) = DB_V2.execute(
            session,
            sql,
            dict(
                vc_id=vendor_customer_id,
                p_id=product_id,
                pc_id=pricing_class_id,
            ),
        ).one()
        data = {
            "id": existing_id,
            "type": "vendor-pricing-by-customer",
            "attributes": {
                "deleted-at": None,
                "price": new_price,
            },
            "relationships": new_obj.data.relationships.model_dump(exclude_none=True)
            | {"vendors": {"data": {"type": "vendors", "id": vendor_id}}},
        }
        return await mod_vendor_pricing_by_customer(
            token, session, existing_id, ModVendorPricingByCustomer(data=data)
        )


@vendor_pricing_by_customer.patch(
    "/{vendor_pricing_by_customer_id}",
    response_model=VendorPricingByCustomerResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    mod_data: ModVendorPricingByCustomer,
) -> VendorPricingByCustomerResourceResp:
    vendor_customer_id = mod_data.data.relationships.vendor_customers.data.pop().id
    vendor_id = mod_data.data.relationships.vendors.data.pop().id
    return (
        auth.VendorCustomerOperations(
            token, VendorPricingByCustomer, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_pricing_by_customer_id,
            primary_id=vendor_customer_id,
        )
    )


@vendor_pricing_by_customer.delete(
    "/{vendor_pricing_by_customer_id}",
    tags=["jsonapi"],
)
async def del_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
    vendor_customer_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorCustomerOperations(
            token, VendorPricingByCustomer, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(
            session, obj_id=vendor_pricing_by_customer_id, primary_id=vendor_customer_id
        )
    )


## NOT IMPLEMENTED ##


@vendor_pricing_by_customer.get("", tags=["jsonapi"])
async def vendor_pricing_by_customer_collection(
    token: Token, session: NewSession
) -> VendorPricingByCustomerResourceResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer.get("/{vendor_pricing_by_customer_id}", tags=["jsonapi"])
async def vendor_pricing_by_customer_resource(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
) -> VendorPricingByCustomerResourceResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/vendor-customers", tags=["jsonapi"]
)
async def vendor_pricing_by_customer_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/relationships/vendor-customers", tags=["jsonapi"]
)
async def vendor_pricing_by_customer_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/vendor-products", tags=["jsonapi"]
)
async def vendor_pricing_by_customer_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/relationships/vendor-products",
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/vendor-pricing-by-customer-attrs",
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_related_vendor_pricing_by_customer_attrs(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/relationships/vendor-pricing-by-customer-attrs",
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_relationships_vendor_pricing_by_customer_attrs(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/vendor-pricing-classes",
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_related_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/relationships/vendor-pricing-classes",
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_relationships_vendor_pricing_classes(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/vendor-pricing-by-customer-changelog",
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_related_vendor_pricing_by_customer_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/relationships/vendor-pricing-by-customer-changelog",
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_relationships_vendor_pricing_by_customer_changelog(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/customer-pricing-by-customer",
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_related_customer_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_pricing_by_customer.get(
    "/{vendor_pricing_by_customer_id}/relationships/customer-pricing-by-customer",
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_relationships_customer_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
