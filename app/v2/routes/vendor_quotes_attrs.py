
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorQuoteAttrResp,
    VendorQuoteAttrQuery,
    VendorQuoteAttrQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorQuoteAttr

PARENT_PREFIX = "/vendors/v2"
VENDOR_QUOTES_ATTRS = VendorQuoteAttr.__jsonapi_type_override__

vendor_quotes_attrs = APIRouter(
    prefix=f"/{VENDOR_QUOTES_ATTRS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorQuoteAttrQueryJSONAPI)


@vendor_quotes_attrs.get(
    "",
    response_model=VendorQuoteAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quotes_attr_collection(
    token: Token, session: NewSession, query: VendorQuoteAttrQuery = Depends()
) -> VendorQuoteAttrResp:
    return (
        auth.VOperations(token, VendorQuoteAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_quotes_attrs.get(
    "/{vendor_quotes_attr_id}",
    response_model=VendorQuoteAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quotes_attr_resource(
    token: Token,
    session: NewSession,
    vendor_quotes_attr_id: int,
    query: VendorQuoteAttrQuery = Depends(),
) -> VendorQuoteAttrResp:
    return (
        auth.VOperations(token, VendorQuoteAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quotes_attr_id)
    )


@vendor_quotes_attrs.get(
    "/{vendor_quotes_attr_id}/vendor-quotes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quotes_attr_related_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_quotes_attr_id: int,
    query: VendorQuoteAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuoteAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quotes_attr_id, "vendor-quotes")
    )

@vendor_quotes_attrs.get(
    "/{vendor_quotes_attr_id}/relationships/vendor-quotes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quotes_attr_relationships_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_quotes_attr_id: int,
    query: VendorQuoteAttrQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuoteAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quotes_attr_id, "vendor-quotes", True)
    )

    

from app.v2.models import ModVendorQuoteAttr

@vendor_quotes_attrs.patch(
    "/{vendor_quotes_attr_id}",
    response_model=VendorQuoteAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_quotes_attr(
    token: Token,
    session: NewSession,
    vendor_quotes_attr_id: int,
    mod_data: ModVendorQuoteAttr,
) -> VendorQuoteAttrResp:
    return (
        auth.VOperations(token, VendorQuoteAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_quotes_attr_id,
                primary_id=mod_data.data.relationships.vendor_quotess.data.id
            )
        )

        
@vendor_quotes_attrs.delete(
    "/{vendor_quotes_attr_id}",
    tags=["jsonapi"],
)
async def del_vendor_quotes_attr(
    token: Token,
    session: NewSession,
    vendor_quotes_attr_id: int,
    vendor_quotes_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorQuoteAttr, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_quotes_attr_id, primary_id=vendor_quotes_id)
    )
    