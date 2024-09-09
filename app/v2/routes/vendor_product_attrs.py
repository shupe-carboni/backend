
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorProductAttrResp,
    VendorProductAttrQuery,
    VendorProductAttrQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorProductAttr

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRODUCT_ATTRS = VendorProductAttr.__jsonapi_type_override__

vendor_product_attrs = APIRouter(
    prefix=f"/{VENDOR_PRODUCT_ATTRS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorProductAttrQueryJSONAPI)


@vendor_product_attrs.get(
    "",
    response_model=VendorProductAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_attr_collection(
    token: Token, session: NewSession, query: VendorProductAttrQuery = Depends()
) -> VendorProductAttrResp:
    return (
        auth.VOperations(token, VendorProductAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_product_attrs.get(
    "/{vendor_product_attr_id}",
    response_model=VendorProductAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_attr_resource(
    token: Token,
    session: NewSession,
    vendor_product_attr_id: int,
    query: VendorProductAttrQuery = Depends(),
) -> VendorProductAttrResp:
    return (
        auth.VOperations(token, VendorProductAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_attr_id)
    )


@vendor_product_attrs.get(
    "/{vendor_product_attr_id}/vendor-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_attr_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_product_attr_id: int,
    query: VendorProductAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_attr_id, "vendor-products")
    )

@vendor_product_attrs.get(
    "/{vendor_product_attr_id}/relationships/vendor-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_attr_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_product_attr_id: int,
    query: VendorProductAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProductAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_attr_id, "vendor-products", True)
    )

    

from app.v2.models import ModVendorProductAttr

@vendor_product_attrs.patch(
    "/{vendor_product_attr_id}",
    response_model=VendorProductAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_product_attr(
    token: Token,
    session: NewSession,
    vendor_product_attr_id: int,
    mod_data: ModVendorProductAttr,
) -> VendorProductAttrResp:
    return (
        auth.VOperations(token, VendorProductAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_product_attr_id,
                primary_id=mod_data.data.relationships.vendor_products.data.id
            )
        )

        
@vendor_product_attrs.delete(
    "/{vendor_product_attr_id}",
    tags=["jsonapi"],
)
async def del_vendor_product_attr(
    token: Token,
    session: NewSession,
    vendor_product_attr_id: int,
    vendor_product_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorProductAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_product_attr_id, primary_id=vendor_product_id)
    )
    