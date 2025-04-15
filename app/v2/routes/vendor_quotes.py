from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.v2.models import VendorQuoteResourceResp, ModVendorQuote, NewVendorQuote
from app.jsonapi.sqla_models import VendorQuote

PARENT_PREFIX = "/vendors"
VENDOR_QUOTES = VendorQuote.__jsonapi_type_override__

vendor_quotes = APIRouter(prefix=f"/{VENDOR_QUOTES}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@vendor_quotes.post(
    "",
    response_model=VendorQuoteResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_quote(
    token: Token,
    session: NewSession,
    new_obj: NewVendorQuote,
) -> VendorQuoteResourceResp:
    vendor_customer_id = new_obj.data.relationships.vendor_customers.data.id
    vendor_id = new_obj.data.relationships.vendors.data.id
    return (
        auth.VendorCustomerOperations(
            token, VendorQuote, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .post(
            session=session,
            data=new_obj.model_dump(exclude_none=True, by_alias=True),
            primary_id=vendor_customer_id,
        )
    )


@vendor_quotes.patch(
    "/{vendor_quote_id}",
    response_model=VendorQuoteResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_quote(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
    mod_data: ModVendorQuote,
) -> VendorQuoteResourceResp:
    vendor_customer_id = mod_data.data.relationships.vendor_customers.data.id
    vendor_id = mod_data.data.relationships.vendors.data.id
    return (
        auth.VendorCustomerOperations(
            token, VendorQuote, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_quote_id,
            primary_id=vendor_customer_id,
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
    vendor_id: str,
) -> None:
    return (
        auth.VendorCustomerOperations(
            token, VendorQuote, PARENT_PREFIX, vendor_id=vendor_id
        )
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_quote_id, primary_id=vendor_customer_id)
    )


## NOT IMPLEMENTED ##


@vendor_quotes.get(
    "",
    tags=["jsonapi"],
)
async def vendor_quote_collection(token: Token, session: NewSession):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes.get(
    "/{vendor_quote_id}",
    tags=["jsonapi"],
)
async def vendor_quote_resource(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes.get(
    "/{vendor_quote_id}/vendor-customers",
    tags=["jsonapi"],
)
async def vendor_quote_related_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes.get(
    "/{vendor_quote_id}/relationships/vendor-customers",
    tags=["jsonapi"],
)
async def vendor_quote_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes.get(
    "/{vendor_quote_id}/vendor-quote-products",
    tags=["jsonapi"],
)
async def vendor_quote_related_vendor_quote_products(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes.get(
    "/{vendor_quote_id}/relationships/vendor-quote-products",
    tags=["jsonapi"],
)
async def vendor_quote_relationships_vendor_quote_products(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes.get(
    "/{vendor_quote_id}/places",
    tags=["jsonapi"],
)
async def vendor_quote_related_places(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes.get(
    "/{vendor_quote_id}/relationships/places",
    tags=["jsonapi"],
)
async def vendor_quote_relationships_places(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes.get(
    "/{vendor_quote_id}/vendor-quotes-changelog",
    tags=["jsonapi"],
)
async def vendor_quote_related_vendor_quotes_changelog(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes.get(
    "/{vendor_quote_id}/relationships/vendor-quotes-changelog",
    tags=["jsonapi"],
)
async def vendor_quote_relationships_vendor_quotes_changelog(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes.get(
    "/{vendor_quote_id}/vendor-quotes-attrs",
    tags=["jsonapi"],
)
async def vendor_quote_related_vendor_quotes_attrs(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_quotes.get(
    "/{vendor_quote_id}/relationships/vendor-quotes-attrs",
    tags=["jsonapi"],
)
async def vendor_quote_relationships_vendor_quotes_attrs(
    token: Token,
    session: NewSession,
    vendor_quote_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
