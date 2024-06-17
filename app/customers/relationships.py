from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app import auth
from app.db import SCA_DB
from app.customers.locations.models import (
    RelatedLocationResponse,
    LocationRelationshipsResponse,
)
from app.adp.models import (
    RelatedCustomerResponse,
    CustomersRelResp,
    RelatedADPCustomerTermsResp,
    ADPCustomerTermsRelationshipsResp,
)
from app.jsonapi.sqla_models import (
    SCACustomer,
    SCACustomerLocation,
    ADPCustomer,
    ADPCustomerTerms,
)

API_TYPE = SCACustomer.__jsonapi_type_override__
customer_rel = APIRouter(tags=[API_TYPE])

CustomersPerm = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]


@customer_rel.get(
    "/{customer_id}/customer-locations",
    response_model=RelatedLocationResponse,
    response_model_exclude_none=True,
)
async def related_location(
    session: NewSession,
    customer_id: int,
    token: CustomersPerm,
) -> RelatedLocationResponse:
    return (
        auth.CustomersOperations(token, API_TYPE)
        .allow_admin()
        .allow_dev()
        .allow_sca()
        .allow_customer("admin")
        .get(
            session=session,
            obj_id=customer_id,
            relationship=False,
            related_resource=SCACustomerLocation.__jsonapi_type_override__,
        )
    )


@customer_rel.get(
    "/{customer_id}/relationships/customer-locations",
    response_model=LocationRelationshipsResponse,
    response_model_exclude_none=True,
)
async def customer_location_relationships(
    session: NewSession,
    customer_id: int,
    token: CustomersPerm,
) -> LocationRelationshipsResponse:
    return (
        auth.CustomersOperations(token, API_TYPE)
        .allow_admin()
        .allow_dev()
        .allow_sca()
        .allow_customer("admin")
        .get(
            session=session,
            obj_id=customer_id,
            relationship=True,
            related_resource=SCACustomerLocation.__jsonapi_type_override__,
        )
    )


@customer_rel.get(
    "/{customer_id}/adp-customers",
    response_model=RelatedCustomerResponse,
    response_model_exclude_none=True,
)
async def related_adp_customers(
    session: NewSession,
    customer_id: int,
    token: CustomersPerm,
) -> RelatedCustomerResponse:
    return (
        auth.CustomersOperations(token, API_TYPE)
        .allow_admin()
        .allow_dev()
        .allow_sca()
        .allow_customer("admin")
        .get(
            session=session,
            obj_id=customer_id,
            relationship=False,
            related_resource=ADPCustomer.__jsonapi_type_override__,
        )
    )


@customer_rel.get(
    "/{customer_id}/relationships/adp-customers",
    response_model=CustomersRelResp,
    response_model_exclude_none=True,
)
async def adp_customer_relationships(
    session: NewSession,
    customer_id: int,
    token: CustomersPerm,
) -> CustomersRelResp:
    return (
        auth.CustomersOperations(token, API_TYPE)
        .allow_admin()
        .allow_dev()
        .allow_sca()
        .allow_customer("admin")
        .get(
            session=session,
            obj_id=customer_id,
            relationship=True,
            related_resource=ADPCustomer.__jsonapi_type_override__,
        )
    )


@customer_rel.get(
    "/{customer_id}/adp-customer-terms",
    response_model=RelatedADPCustomerTermsResp,
    response_model_exclude_none=True,
)
async def related_adp_customer_terms(
    session: NewSession,
    customer_id: int,
    token: CustomersPerm,
) -> RelatedADPCustomerTermsResp:

    return (
        auth.CustomersOperations(token, API_TYPE)
        .allow_admin()
        .allow_dev()
        .allow_sca()
        .allow_customer("admin")
        .get(
            session=session,
            obj_id=customer_id,
            relationship=False,
            related_resource=ADPCustomerTerms.__jsonapi_type_override__,
        )
    )


@customer_rel.get(
    "/{customer_id}/relationships/adp-customer-terms",
    response_model=ADPCustomerTermsRelationshipsResp,
    response_model_exclude_none=True,
)
async def adp_customer_terms_relationships(
    session: NewSession,
    customer_id: int,
    token: CustomersPerm,
) -> ADPCustomerTermsRelationshipsResp:
    return (
        auth.CustomersOperations(token, API_TYPE)
        .allow_admin()
        .allow_dev()
        .allow_sca()
        .allow_customer("admin")
        .get(
            session=session,
            obj_id=customer_id,
            relationship=True,
            related_resource=ADPCustomerTerms.__jsonapi_type_override__,
        )
    )
