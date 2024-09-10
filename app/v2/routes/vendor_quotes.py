
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorQuoteResp,
    VendorQuoteQuery,
    VendorQuoteQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorQuote

PARENT_PREFIX = "/vendors/v2"
VENDOR_QUOTES = VendorQuote.__jsonapi_type_override__

vendor_quotes = APIRouter(
    prefix=f"/{VENDOR_QUOTES}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorQuoteQueryJSONAPI)


@vendor_quotes.get(
    "",
    response_model=VendorQuoteResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_collection(
    token: Token, session: NewSession, query: VendorQuoteQuery = Depends()
) -> VendorQuoteResp:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_quotes.get(
    "/{vendor_quote_id}",
    response_model=VendorQuoteResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_resource(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    query: VendorQuoteQuery = Depends(),
) -> VendorQuoteResp:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_id)
    )


@vendor_quotes.get(
    "/{vendor_quote_id}/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    query: VendorQuoteQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_id, "vendor-customers")
    )

@vendor_quotes.get(
    "/{vendor_quote_id}/relationships/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    query: VendorQuoteQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_id, "vendor-customers", True)
    )

    
@vendor_quotes.get(
    "/{vendor_quote_id}/vendor-quote-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_related_vendor_quote_products(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    query: VendorQuoteQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_id, "vendor-quote-products")
    )

@vendor_quotes.get(
    "/{vendor_quote_id}/relationships/vendor-quote-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_relationships_vendor_quote_products(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    query: VendorQuoteQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_id, "vendor-quote-products", True)
    )

    
@vendor_quotes.get(
    "/{vendor_quote_id}/places",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_related_places(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    query: VendorQuoteQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_id, "places")
    )

@vendor_quotes.get(
    "/{vendor_quote_id}/relationships/places",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_relationships_places(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    query: VendorQuoteQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_id, "places", True)
    )

    
@vendor_quotes.get(
    "/{vendor_quote_id}/vendor-quotes-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_related_vendor_quotes_changelog(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    query: VendorQuoteQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_id, "vendor-quotes-changelog")
    )

@vendor_quotes.get(
    "/{vendor_quote_id}/relationships/vendor-quotes-changelog",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_relationships_vendor_quotes_changelog(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    query: VendorQuoteQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_id, "vendor-quotes-changelog", True)
    )

    
@vendor_quotes.get(
    "/{vendor_quote_id}/vendor-quotes-attrs",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_related_vendor_quotes_attrs(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    query: VendorQuoteQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_id, "vendor-quotes-attrs")
    )

@vendor_quotes.get(
    "/{vendor_quote_id}/relationships/vendor-quotes-attrs",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_quote_relationships_vendor_quotes_attrs(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    query: VendorQuoteQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_quote_id, "vendor-quotes-attrs", True)
    )

    

from app.v2.models import ModVendorQuote

@vendor_quotes.patch(
    "/{vendor_quote_id}",
    response_model=VendorQuoteResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_quote(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    mod_data: ModVendorQuote,
) -> VendorQuoteResp:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_quote_id,
                primary_id=mod_data.data.relationships.vendor_customers.data.id
            )
        )

        
@vendor_quotes.delete(
    "/{vendor_quote_id}",
    tags=["jsonapi"],
)
async def del_vendor_quote(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    vendor_customer_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_quote_id, primary_id=vendor_customer_id)
    )
    