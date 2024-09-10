
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    CustomerLocationMappingResp,
    CustomerLocationMappingQuery,
    CustomerLocationMappingQueryJSONAPI,
)
from app.jsonapi.sqla_models import CustomerLocationMapping

PARENT_PREFIX = "/vendors/v2"
CUSTOMER_LOCATION_MAPPING = CustomerLocationMapping.__jsonapi_type_override__

customer_location_mapping = APIRouter(
    prefix=f"/{CUSTOMER_LOCATION_MAPPING}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(CustomerLocationMappingQueryJSONAPI)


@customer_location_mapping.get(
    "",
    response_model=CustomerLocationMappingResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_location_mapping_collection(
    token: Token, session: NewSession, query: CustomerLocationMappingQuery = Depends()
) -> CustomerLocationMappingResp:
    return (
        auth.VOperations(token, CustomerLocationMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@customer_location_mapping.get(
    "/{customer_location_mapping_id}",
    response_model=CustomerLocationMappingResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_location_mapping_resource(
    token: Token,
    session: NewSession,
    customer_location_mapping_id: int,
    query: CustomerLocationMappingQuery = Depends(),
) -> CustomerLocationMappingResp:
    return (
        auth.VOperations(token, CustomerLocationMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_location_mapping_id)
    )


@customer_location_mapping.get(
    "/{customer_location_mapping_id}/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_location_mapping_related_vendor_customers(
    token: Token,
    session: NewSession,
    customer_location_mapping_id: int,
    query: CustomerLocationMappingQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, CustomerLocationMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_location_mapping_id, "vendor-customers")
    )

@customer_location_mapping.get(
    "/{customer_location_mapping_id}/relationships/vendor-customers",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_location_mapping_relationships_vendor_customers(
    token: Token,
    session: NewSession,
    customer_location_mapping_id: int,
    query: CustomerLocationMappingQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, CustomerLocationMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_location_mapping_id, "vendor-customers", True)
    )

    
@customer_location_mapping.get(
    "/{customer_location_mapping_id}/customer-locations",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_location_mapping_related_customer_locations(
    token: Token,
    session: NewSession,
    customer_location_mapping_id: int,
    query: CustomerLocationMappingQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, CustomerLocationMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_location_mapping_id, "customer-locations")
    )

@customer_location_mapping.get(
    "/{customer_location_mapping_id}/relationships/customer-locations",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def customer_location_mapping_relationships_customer_locations(
    token: Token,
    session: NewSession,
    customer_location_mapping_id: int,
    query: CustomerLocationMappingQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, CustomerLocationMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), customer_location_mapping_id, "customer-locations", True)
    )

    

from app.v2.models import ModCustomerLocationMapping

@customer_location_mapping.patch(
    "/{customer_location_mapping_id}",
    response_model=CustomerLocationMappingResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_customer_location_mapping(
    token: Token,
    session: NewSession,
    customer_location_mapping_id: int,
    mod_data: ModCustomerLocationMapping,
) -> CustomerLocationMappingResp:
    return (
        auth.VOperations(token, CustomerLocationMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=customer_location_mapping_id,
    
            )
        )

        
@customer_location_mapping.delete(
    "/{customer_location_mapping_id}",
    tags=["jsonapi"],
)
async def del_customer_location_mapping(
    token: Token,
    session: NewSession,
    customer_location_mapping_id: int,
    
) -> None:
    return (
        auth.VOperations(token, CustomerLocationMapping, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=customer_location_mapping_id)
    )
    