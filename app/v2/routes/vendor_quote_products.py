
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorQuoteProductResp,
    VendorQuoteProductQuery,
    VendorQuoteProductQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorQuoteProduct

PARENT_PREFIX = "/vendors/v2"
VENDOR_QUOTE_PRODUCTS = VendorQuoteProduct.__jsonapi_type_override__

vendor_quote_products = APIRouter(
    prefix=f"/{VENDOR_QUOTE_PRODUCTS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorQuoteProductQueryJSONAPI)


@vendor_quote_products.get(
    "",
    response_model=VendorQuoteProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_product_collection(
    token: Token, session: NewSession, query: VendorQuoteProductQuery = Depends()
) -> VendorQuoteProductResp:
    return (
        auth.VOperations(token, VendorQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_quote_products.get(
    "/{vendor_quote_product_id}",
    response_model=VendorQuoteProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_product_resource(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
    query: VendorQuoteProductQuery = Depends(),
) -> VendorQuoteProductResp:
    return (
        auth.VOperations(token, VendorQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_product_id)
    )


@vendor_quote_products.get(
    "/{vendor_quote_product_id}/vendor-quotes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_product_related_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
    query: VendorQuoteProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_product_id, "vendor-quotes")
    )

@vendor_quote_products.get(
    "/{vendor_quote_product_id}/relationships/vendor-quotes",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_product_relationships_vendor_quotes(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
    query: VendorQuoteProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_product_id, "vendor-quotes", True)
    )

    
@vendor_quote_products.get(
    "/{vendor_quote_product_id}/vendor-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_product_related_vendor_products(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
    query: VendorQuoteProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_product_id, "vendor-products")
    )

@vendor_quote_products.get(
    "/{vendor_quote_product_id}/relationships/vendor-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_product_relationships_vendor_products(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
    query: VendorQuoteProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_product_id, "vendor-products", True)
    )

    
@vendor_quote_products.get(
    "/{vendor_quote_product_id}/vendor-quote-products-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_product_related_vendor_quote_products_changelog(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
    query: VendorQuoteProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_product_id, "vendor-quote-products-changelog")
    )

@vendor_quote_products.get(
    "/{vendor_quote_product_id}/relationships/vendor-quote-products-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_product_relationships_vendor_quote_products_changelog(
    token: Token,
    session: NewSession,
    vendor_quote_product_id: int,
    query: VendorQuoteProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_product_id, "vendor-quote-products-changelog", True)
    )

    

from app.v2.models import ModVendorQuoteProduct

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
    return (
        auth.VOperations(token, VendorQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_quote_product_id,
                primary_id=mod_data.data.relationships.vendor_quotes.data.id
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
    vendor_quote_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorQuoteProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_quote_product_id, primary_id=vendor_quote_id)
    )
    