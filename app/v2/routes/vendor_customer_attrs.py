
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorCustomerAttrResp,
    VendorCustomerAttrQuery,
    VendorCustomerAttrQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorCustomerAttr

PARENT_PREFIX = "/vendors/v2"
VENDOR_CUSTOMER_ATTRS = VendorCustomerAttr.__jsonapi_type_override__

vendor_customer_attrs = APIRouter(
    prefix=f"/{VENDOR_CUSTOMER_ATTRS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorCustomerAttrQueryJSONAPI)


@vendor_customer_attrs.get(
    "",
    response_model=VendorCustomerAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_attr_collection(
    token: Token, session: NewSession, query: VendorCustomerAttrQuery = Depends()
) -> VendorCustomerAttrResp:
    return (
        auth.VOperations(token, VendorCustomerAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_customer_attrs.get(
    "/{vendor_customer_attr_id}",
    response_model=VendorCustomerAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_attr_resource(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
    query: VendorCustomerAttrQuery = Depends(),
) -> VendorCustomerAttrResp:
    return (
        auth.VOperations(token, VendorCustomerAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_attr_id)
    )


@vendor_customer_attrs.get(
    "/{vendor_customer_attr_id}/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_attr_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
    query: VendorCustomerAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomerAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_attr_id, "vendor-customers")
    )

@vendor_customer_attrs.get(
    "/{vendor_customer_attr_id}/relationships/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_attr_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
    query: VendorCustomerAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomerAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_attr_id, "vendor-customers", True)
    )

    
@vendor_customer_attrs.get(
    "/{vendor_customer_attr_id}/vendor-customer-attrs-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_attr_related_vendor_customer_attrs_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
    query: VendorCustomerAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomerAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_attr_id, "vendor-customer-attrs-changelog")
    )

@vendor_customer_attrs.get(
    "/{vendor_customer_attr_id}/relationships/vendor-customer-attrs-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_customer_attr_relationships_vendor_customer_attrs_changelog(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
    query: VendorCustomerAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorCustomerAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_customer_attr_id, "vendor-customer-attrs-changelog", True)
    )

    

from app.v2.models import ModVendorCustomerAttr

@vendor_customer_attrs.patch(
    "/{vendor_customer_attr_id}",
    response_model=VendorCustomerAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_customer_attr(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
    mod_data: ModVendorCustomerAttr,
) -> VendorCustomerAttrResp:
    return (
        auth.VOperations(token, VendorCustomerAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_customer_attr_id,
                primary_id=mod_data.data.relationships.vendor_customers.data.id
            )
        )

        
@vendor_customer_attrs.delete(
    "/{vendor_customer_attr_id}",
    tags=["jsonapi"],
)
async def del_vendor_customer_attr(
    token: Token,
    session: NewSession,
    vendor_customer_attr_id: int,
    vendor_customer_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorCustomerAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_customer_attr_id, primary_id=vendor_customer_id)
    )
    