"""
Customer Locations Routes
"""

import logging
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app import auth
from app.customers.locations.models import (
    LocationResponse,
    LocationQueryJSONAPI,
    LocationQuery,
    NewLocation,
    ModLocation,
    RelatedADPAliasToSCACustomerLocation,
)
from app.db.db import SCA_DB
from app.jsonapi.sqla_models import SCACustomerLocation
from app.jsonapi.core_models import convert_query

PARENT_PREFIX = "/customers"
API_TYPE = SCACustomerLocation.__jsonapi_type_override__
customer_locations = APIRouter(prefix=f"/{API_TYPE}", tags=["customer-locations"])
logger = logging.getLogger("uvicorn.info")

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(LocationQueryJSONAPI)


@customer_locations.get(
    "",
    response_model=LocationResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_locations_collection(
    session: NewSession, token: Token, query: LocationQuery = Depends()
) -> LocationResponse:

    return (
        auth.CustomersOperations(token, SCACustomerLocation, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("manager")
        .get(session=session, query=converter(query))
    )


@customer_locations.get(
    "/{customer_location_id}",
    response_model=LocationResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_location(
    session: NewSession,
    token: Token,
    customer_location_id: int,
    query: LocationQuery = Depends(),
) -> LocationResponse:
    return (
        auth.CustomersOperations(token, SCACustomerLocation, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("manager")
        .get(
            session=session,
            query=converter(query),
            obj_id=customer_location_id,
        )
    )


@customer_locations.get(
    "/{customer_location_id}/adp-alias-to-sca-customer-locations",
    response_model=RelatedADPAliasToSCACustomerLocation,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_location_adp_alias(
    session: NewSession,
    token: Token,
    customer_location_id: int,
    query: LocationQuery = Depends(),
) -> RelatedADPAliasToSCACustomerLocation:
    return (
        auth.CustomersOperations(token, SCACustomerLocation, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("manager")
        .get(
            session=session,
            query=converter(query),
            obj_id=customer_location_id,
            related_resource="adp-alias-to-sca-customer-locations",
        )
    )


@customer_locations.post(
    "",
    response_model=LocationResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_customer_location(
    session: NewSession, token: Token, new_customer_location: NewLocation
) -> LocationResponse:
    return (
        auth.CustomersOperations(token, SCACustomerLocation, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("admin")
        .post(
            session=session,
            data=new_customer_location.model_dump(exclude_none=True, by_alias=True),
            primary_id=new_customer_location.data.relationships.customers.data.id,
        )
    )


@customer_locations.patch(
    "/{customer_location_id}",
    response_model=LocationResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_customer_location(
    session: NewSession,
    token: Token,
    customer_location_id: int,
    mod_customer_location: ModLocation,
) -> LocationResponse:
    return (
        auth.CustomersOperations(token, SCACustomerLocation, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("admin")
        .patch(
            session=session,
            data=mod_customer_location.model_dump(exclude_none=True, by_alias=True),
            primary_id=mod_customer_location.data.relationships.customers.data.id,
            obj_id=customer_location_id,
        )
    )


@customer_locations.delete("/{customer_location_id}", tags=["jsonapi"])
async def del_customer_location(
    session: NewSession, token: Token, customer_location_id: int, customer_id: int
) -> None:
    return (
        auth.CustomersOperations(token, SCACustomerLocation, prefix=PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("admin")
        .delete(
            session=session,
            obj_id=customer_location_id,
            primary_id=customer_id,
        )
    )
