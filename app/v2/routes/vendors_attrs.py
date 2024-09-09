
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorsAttrResp,
    VendorsAttrQuery,
    VendorsAttrQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorsAttr

PARENT_PREFIX = "/vendors/v2"
VENDORS_ATTRS = VendorsAttr.__jsonapi_type_override__

vendors_attrs = APIRouter(
    prefix=f"/{VENDORS_ATTRS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorsAttrQueryJSONAPI)


@vendors_attrs.get(
    "",
    response_model=VendorsAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendors_attr_collection(
    token: Token, session: NewSession, query: VendorsAttrQuery = Depends()
) -> VendorsAttrResp:
    return (
        auth.VOperations(token, VendorsAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendors_attrs.get(
    "/{vendors_attr_id}",
    response_model=VendorsAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendors_attr_resource(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
    query: VendorsAttrQuery = Depends(),
) -> VendorsAttrResp:
    return (
        auth.VOperations(token, VendorsAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendors_attr_id)
    )


@vendors_attrs.get(
    "/{vendors_attr_id}/vendors",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendors_attr_related_vendors(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
    query: VendorsAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorsAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendors_attr_id, "vendors")
    )

@vendors_attrs.get(
    "/{vendors_attr_id}/relationships/vendors",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendors_attr_relationships_vendors(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
    query: VendorsAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorsAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendors_attr_id, "vendors", True)
    )

    
@vendors_attrs.get(
    "/{vendors_attr_id}/vendors-attrs-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendors_attr_related_vendors_attrs_changelog(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
    query: VendorsAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorsAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendors_attr_id, "vendors-attrs-changelog")
    )

@vendors_attrs.get(
    "/{vendors_attr_id}/relationships/vendors-attrs-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendors_attr_relationships_vendors_attrs_changelog(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
    query: VendorsAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorsAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendors_attr_id, "vendors-attrs-changelog", True)
    )

    

from app.v2.models import ModVendorsAttr

@vendors_attrs.patch(
    "/{vendors_attr_id}",
    response_model=VendorsAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendors_attr(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
    mod_data: ModVendorsAttr,
) -> VendorsAttrResp:
    return (
        auth.VOperations(token, VendorsAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendors_attr_id,
                primary_id=mod_data.data.relationships.vendors.data.id
            )
        )

        
@vendors_attrs.delete(
    "/{vendors_attr_id}",
    tags=["jsonapi"],
)
async def del_vendors_attr(
    token: Token,
    session: NewSession,
    vendors_attr_id: int,
    vendor_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorsAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendors_attr_id, primary_id=vendor_id)
    )
    