from typing import Annotated
from fastapi import HTTPException, Depends, status
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.adp.models import (
    CustomersResp,
    CustomersQuery,
    CustomersQueryJSONAPI,
    RelatedCoilProgResp,
    CoilProgRelResp,
    RelatedAirHandlerProgResp,
    AirHandlerProgRelResp,
    RatingsRelResp,
    RelatedRatingsResponse,
    PartsRelResp,
    RelatedPartsResponse,
)
from app.jsonapi.sqla_models import (
    ADPCustomer,
    ADPCoilProgram,
    ADPAHProgram,
    ADPProgramRating,
    ADPProgramPart,
)
from app.jsonapi.core_models import convert_query

ADP_CUSTOMERS = ADPCustomer.__jsonapi_type_override__
ADP_COIL_PROGS = ADPCoilProgram.__jsonapi_type_override__
ADP_AH_PROGS = ADPAHProgram.__jsonapi_type_override__
ADP_PROG_RATINGS = ADPProgramRating.__jsonapi_type_override__
ADP_PROG_PARTS = ADPProgramPart.__jsonapi_type_override__

adp_customers = APIRouter(prefix=f"/{ADP_CUSTOMERS}", tags=["customers"])

ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(CustomersQueryJSONAPI)


@adp_customers.get(
    "", response_model=CustomersResp, response_model_exclude_none=True, tags=["jsonapi"]
)
def all_adp_customers(
    token: ADPPerm, session: NewSession, query: CustomersQuery = Depends()
) -> CustomersResp:
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session=session, resource=ADP_CUSTOMERS, query=converter(query))
    )


@adp_customers.get(
    "/{customer_id}",
    response_model=CustomersResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def adp_customer(
    token: ADPPerm,
    session: NewSession,
    customer_id: int,
    query: CustomersQuery = Depends(),
) -> CustomersResp:
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=ADP_CUSTOMERS,
            query=converter(query),
            obj_id=customer_id,
        )
    )


@adp_customers.get(
    "/{customer_id}/adp-coil-programs",
    response_model=RelatedCoilProgResp,
    response_model_exclude_none=True,
)
async def related_coil_programs(
    session: NewSession,
    customer_id: int,
    token: ADPPerm,
) -> RelatedCoilProgResp:
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=ADP_CUSTOMERS,
            query={},
            obj_id=customer_id,
            relationship=False,
            related_resource=ADP_COIL_PROGS,
        )
    )


@adp_customers.get(
    "/{customer_id}/relationships/adp-coil-programs",
    response_model=CoilProgRelResp,
    response_model_exclude_none=True,
)
async def coil_programs_relationships(
    session: NewSession,
    customer_id: int,
    token: ADPPerm,
) -> CoilProgRelResp:
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=ADP_CUSTOMERS,
            query={},
            obj_id=customer_id,
            relationship=True,
            related_resource=ADP_COIL_PROGS,
        )
    )


@adp_customers.get(
    "/{customer_id}/adp-ah-programs",
    response_model=RelatedAirHandlerProgResp,
    response_model_exclude_none=True,
)
async def related_ah_programs(
    session: NewSession,
    customer_id: int,
    token: ADPPerm,
) -> RelatedAirHandlerProgResp:
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=ADP_CUSTOMERS,
            query={},
            obj_id=customer_id,
            relationship=False,
            related_resource=ADP_AH_PROGS,
        )
    )


@adp_customers.get(
    "/{customer_id}/relationships/adp-ah-programs",
    response_model=AirHandlerProgRelResp,
    response_model_exclude_none=True,
)
async def ah_programs_relationships(
    session: NewSession,
    customer_id: int,
    token: ADPPerm,
) -> AirHandlerProgRelResp:
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=ADP_CUSTOMERS,
            query={},
            obj_id=customer_id,
            relationship=True,
            related_resource=ADP_AH_PROGS,
        )
    )


@adp_customers.get(
    "/{customer_id}/adp-program-ratings",
    response_model=RelatedRatingsResponse,
    response_model_exclude_none=True,
)
async def related_ratings(
    session: NewSession,
    customer_id: int,
    token: ADPPerm,
) -> RelatedRatingsResponse:
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=ADP_CUSTOMERS,
            query={},
            obj_id=customer_id,
            relationship=False,
            related_resource=ADP_PROG_RATINGS,
        )
    )


@adp_customers.get(
    "/{customer_id}/relationships/adp-program-ratings",
    response_model=RatingsRelResp,
    response_model_exclude_none=True,
)
async def ratings_relationships(
    session: NewSession,
    customer_id: int,
    token: ADPPerm,
) -> RatingsRelResp:
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=ADP_CUSTOMERS,
            query={},
            obj_id=customer_id,
            relationship=True,
            related_resource=ADP_PROG_RATINGS,
        )
    )


@adp_customers.get(
    "/{customer_id}/adp-program-parts",
    response_model=RelatedPartsResponse,
    response_model_exclude_none=True,
)
async def related_ratings(
    session: NewSession,
    customer_id: int,
    token: ADPPerm,
) -> RelatedPartsResponse:
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=ADP_CUSTOMERS,
            query={},
            obj_id=customer_id,
            relationship=False,
            related_resource=ADP_PROG_PARTS,
        )
    )


@adp_customers.get(
    "/{customer_id}/relationships/adp-program-parts",
    response_model=PartsRelResp,
    response_model_exclude_none=True,
)
async def ratings_relationships(
    session: NewSession,
    customer_id: int,
    token: ADPPerm,
) -> PartsRelResp:
    return (
        auth.ADPOperations(token)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            resource=ADP_CUSTOMERS,
            query={},
            obj_id=customer_id,
            relationship=True,
            related_resource=ADP_PROG_PARTS,
        )
    )
