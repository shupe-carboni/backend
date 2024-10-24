from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import VendorQuoteAttrResp, ModVendorQuoteAttr, NewVendorQuoteAttr
from app.jsonapi.sqla_models import VendorQuoteAttr

PARENT_PREFIX = "/vendors"
VENDOR_QUOTES_ATTRS = VendorQuoteAttr.__jsonapi_type_override__

vendor_quotes_attrs = APIRouter(prefix=f"/{VENDOR_QUOTES_ATTRS}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_quotes_attrs.post(
    "",
    response_model=VendorQuoteAttrResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_quotes_attr(
    token: Token,
    session: NewSession,
    new_obj: NewVendorQuoteAttr,
) -> VendorQuoteAttrResp:
    vendor_quotes_id = new_obj.data.relationships.vendor_quotes.data.id
    vendor_id = new_obj.data.relationships.vendors.data.id
    return (
        auth.VendorQuoteOperations(
            token, VendorQuoteAttr, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .post(
            session=session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=vendor_quotes_id,
        )
    )


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
    vendor_quotes_id = mod_data.data.relationships.vendor_quotes.data.id
    vendor_id = mod_data.data.relationships.vendors.data.id
    return (
        auth.VendorQuoteOperations(
            token, VendorQuoteAttr, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_quotes_attr_id,
            primary_id=vendor_quotes_id,
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
    vendor_id: str,
) -> None:
    return (
        auth.VendorQuoteOperations(
            token, VendorQuoteAttr, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(session, obj_id=vendor_quotes_attr_id, primary_id=vendor_quotes_id)
    )


@vendor_quotes_attrs.get(
    "",
    tags=["jsonapi"],
)
async def vendor_quotes_attr_collection(
    token: Token, session: NewSession
) -> VendorQuoteAttrResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


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
) -> VendorQuoteAttrResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes_attrs.get(
    "/{vendor_quotes_attr_id}/vendor-quotes",
    tags=["jsonapi"],
)
async def vendor_quotes_attr_related_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_quotes_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes_attrs.get(
    "/{vendor_quotes_attr_id}/relationships/vendor-quotes",
    tags=["jsonapi"],
)
async def vendor_quotes_attr_relationships_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_quotes_attr_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
