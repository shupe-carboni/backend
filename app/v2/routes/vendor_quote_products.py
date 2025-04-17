from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import (
    VendorQuoteProductResp,
    ModVendorQuoteProduct,
    NewVendorQuoteProduct,
)
from app.jsonapi.sqla_models import VendorQuoteProduct

PARENT_PREFIX = "/vendors"
VENDOR_QUOTE_PRODUCTS = VendorQuoteProduct.__jsonapi_type_override__

vendor_quote_products = APIRouter(prefix=f"/{VENDOR_QUOTE_PRODUCTS}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_quote_products.post(
    "",
    response_model=VendorQuoteProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_quote_product(
    token: Token,
    session: NewSession,
    new_obj: NewVendorQuoteProduct,
) -> VendorQuoteProductResp:
    vendor_quotes_id = new_obj.data.relationships.vendor_quotes.data[0].id
    vendor_id = new_obj.data.relationships.vendors.data[0].id
    return (
        auth.VendorQuoteOperations(
            token, VendorQuoteProduct, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .post(
            session=session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=vendor_quotes_id,
        )
    )


@vendor_quote_products.patch(
    "/{vendor_quote_product_id}",
    response_model=VendorQuoteProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_quote_product(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
    mod_data: ModVendorQuoteProduct,
) -> VendorQuoteProductResp:
    vendor_quotes_id = mod_data.data.relationships.vendor_quotes.data[0].id
    vendor_id = mod_data.data.relationships.vendors.data[0].id
    return (
        auth.VendorQuoteOperations(
            token, VendorQuoteProduct, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_quote_product_id,
            primary_id=vendor_quotes_id,
        )
    )


@vendor_quote_products.delete(
    "/{vendor_quote_product_id}",
    tags=["jsonapi"],
)
async def del_vendor_quote_product(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
    vendor_quotes_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorQuoteOperations(
            token, VendorQuoteProduct, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_quote_product_id, primary_id=vendor_quotes_id)
    )


@vendor_quote_products.get("", tags=["Not Implemented"])
async def vendor_quote_product_collection(
    token: Token, session: NewSession
) -> VendorQuoteProductResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quote_products.get("/{vendor_quote_product_id}", tags=["Not Implemented"])
async def vendor_quote_product_resource(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
) -> VendorQuoteProductResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quote_products.get(
    "/{vendor_quote_product_id}/vendor-quotes", tags=["Not Implemented"]
)
async def vendor_quote_product_related_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quote_products.get(
    "/{vendor_quote_product_id}/relationships/vendor-quotes", tags=["Not Implemented"]
)
async def vendor_quote_product_relationships_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quote_products.get(
    "/{vendor_quote_product_id}/vendor-products", tags=["Not Implemented"]
)
async def vendor_quote_product_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quote_products.get(
    "/{vendor_quote_product_id}/relationships/vendor-products", tags=["Not Implemented"]
)
async def vendor_quote_product_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quote_products.get(
    "/{vendor_quote_product_id}/vendor-quote-products-changelog",
    tags=["Not Implemented"],
)
async def vendor_quote_product_related_vendor_quote_products_changelog(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quote_products.get(
    "/{vendor_quote_product_id}/relationships/vendor-quote-products-changelog",
    tags=["Not Implemented"],
)
async def vendor_quote_product_relationships_vendor_quote_products_changelog(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
