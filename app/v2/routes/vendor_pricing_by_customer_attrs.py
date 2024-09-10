
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorPricingByCustomerAttrResp,
    VendorPricingByCustomerAttrQuery,
    VendorPricingByCustomerAttrQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorPricingByCustomerAttr

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRICING_BY_CUSTOMER_ATTRS = VendorPricingByCustomerAttr.__jsonapi_type_override__

vendor_pricing_by_customer_attrs = APIRouter(
    prefix=f"/{VENDOR_PRICING_BY_CUSTOMER_ATTRS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorPricingByCustomerAttrQueryJSONAPI)


@vendor_pricing_by_customer_attrs.get(
    "",
    response_model=VendorPricingByCustomerAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_attr_collection(
    token: Token, session: NewSession, query: VendorPricingByCustomerAttrQuery = Depends()
) -> VendorPricingByCustomerAttrResp:
    return (
        auth.VOperations(token, VendorPricingByCustomerAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_pricing_by_customer_attrs.get(
    "/{vendor_pricing_by_customer_attr_id}",
    response_model=VendorPricingByCustomerAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_attr_resource(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_attr_id: int,
    query: VendorPricingByCustomerAttrQuery = Depends(),
) -> VendorPricingByCustomerAttrResp:
    return (
        auth.VOperations(token, VendorPricingByCustomerAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_attr_id)
    )


@vendor_pricing_by_customer_attrs.get(
    "/{vendor_pricing_by_customer_attr_id}/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_attr_related_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_attr_id: int,
    query: VendorPricingByCustomerAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomerAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_attr_id, "vendor-pricing-by-customer")
    )

@vendor_pricing_by_customer_attrs.get(
    "/{vendor_pricing_by_customer_attr_id}/relationships/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_pricing_by_customer_attr_relationships_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_attr_id: int,
    query: VendorPricingByCustomerAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomerAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_pricing_by_customer_attr_id, "vendor-pricing-by-customer", True)
    )

    
@vendor_pricing_by_customer_attrs.delete(
    "/{vendor_pricing_by_customer_attr_id}",
    tags=["jsonapi"],
)
async def del_vendor_pricing_by_customer_attr(
    token: Token,
    session: NewSession,
    vendor_pricing_by_customer_attr_id: int,
    vendor_pricing_by_customer_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorPricingByCustomerAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_pricing_by_customer_attr_id, primary_id=vendor_pricing_by_customer_id)
    )
    