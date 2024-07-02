from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query

# from app.RELATED_RESOURCE.models import
from app.friedrich.models import (
    FriedrichQuoteResp,
    FriedrichQuoteQuery,
    FriedrichQuoteQueryJSONAPI,
)
from app.jsonapi.sqla_models import FriedrichQuote

PARENT_PREFIX = "/vendors/friedrich"
FRIEDRICH_QUOTES = FriedrichQuote.__jsonapi_type_override__

friedrich_quotes = APIRouter(prefix=f"/{FRIEDRICH_QUOTES}", tags=["friedrich", ""])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(FriedrichQuoteQueryJSONAPI)


@friedrich_quotes.get(
    "",
    response_model=FriedrichQuoteResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_collection(
    token: Token, session: NewSession, query: FriedrichQuoteQuery = Depends()
) -> FriedrichQuoteResp:
    return (
        auth.FriedrichOperations(token, FriedrichQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@friedrich_quotes.get(
    "/{friedrich_quote_id}",
    response_model=FriedrichQuoteResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_resource(
    token: Token,
    session: NewSession,
    friedrich_quote_id: int,
    query: FriedrichQuoteQuery = Depends(),
) -> FriedrichQuoteResp:
    return (
        auth.FriedrichOperations(token, FriedrichQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_quote_id)
    )


@friedrich_quotes.get(
    "/{friedrich_quote_id}/friedrich-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_related_friedrich_customers(
    token: Token,
    session: NewSession,
    friedrich_quote_id: int,
    query: FriedrichQuoteQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_quote_id, "friedrich-customers")
    )


@friedrich_quotes.get(
    "/{friedrich_quote_id}/relationships/friedrich-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_relationships_friedrich_customers(
    token: Token,
    session: NewSession,
    friedrich_quote_id: int,
    query: FriedrichQuoteQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_quote_id, "friedrich-customers", True)
    )


@friedrich_quotes.get(
    "/{friedrich_quote_id}/customer-locations",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_related_customer_locations(
    token: Token,
    session: NewSession,
    friedrich_quote_id: int,
    query: FriedrichQuoteQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_quote_id, "customer-locations")
    )


@friedrich_quotes.get(
    "/{friedrich_quote_id}/relationships/customer-locations",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_relationships_customer_locations(
    token: Token,
    session: NewSession,
    friedrich_quote_id: int,
    query: FriedrichQuoteQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_quote_id, "customer-locations", True)
    )


@friedrich_quotes.get(
    "/{friedrich_quote_id}/places",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_related_places(
    token: Token,
    session: NewSession,
    friedrich_quote_id: int,
    query: FriedrichQuoteQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_quote_id, "places")
    )


@friedrich_quotes.get(
    "/{friedrich_quote_id}/relationships/places",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_relationships_places(
    token: Token,
    session: NewSession,
    friedrich_quote_id: int,
    query: FriedrichQuoteQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_quote_id, "places", True)
    )


@friedrich_quotes.get(
    "/{friedrich_quote_id}/friedrich-quote-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_related_friedrich_quote_products(
    token: Token,
    session: NewSession,
    friedrich_quote_id: int,
    query: FriedrichQuoteQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), friedrich_quote_id, "friedrich-quote-products")
    )


@friedrich_quotes.get(
    "/{friedrich_quote_id}/relationships/friedrich-quote-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def friedrich_quote_relationships_friedrich_quote_products(
    token: Token,
    session: NewSession,
    friedrich_quote_id: int,
    query: FriedrichQuoteQuery = Depends(),
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session,
            converter(query),
            friedrich_quote_id,
            "friedrich-quote-products",
            True,
        )
    )


from app.friedrich.models import ModFriedrichQuote


@friedrich_quotes.patch(
    "/{friedrich_quote_id}",
    response_model=FriedrichQuoteResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_friedrich_quote(
    token: Token,
    session: NewSession,
    friedrich_quote_id: int,
    mod_data: ModFriedrichQuote,
) -> FriedrichQuoteResp:
    return (
        auth.FriedrichOperations(token, FriedrichQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=friedrich_quote_id,
            primary_id=mod_data.data.relationships.friedrich_customers.data.id,
        )
    )


@friedrich_quotes.delete(
    "/{friedrich_quote_id}",
    tags=["jsonapi"],
)
async def del_friedrich_quote(
    token: Token,
    session: NewSession,
    friedrich_quote_id: int,
    friedrich_customer_id: int,
) -> None:
    return (
        auth.FriedrichOperations(token, FriedrichQuote, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=friedrich_quote_id, primary_id=friedrich_customer_id)
    )
