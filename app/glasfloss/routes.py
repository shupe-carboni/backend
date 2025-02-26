import logging
from typing import Annotated, Optional
from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends, status

from app import auth
from app.db import Session, DB_V2
from app.v2.models import VendorCustomer
from app.glasfloss.parsing import FilterModel, Filter, ModelType, FilterBuilt

glasfloss = APIRouter(prefix=f"/glasfloss", tags=["glasfloss"])
logger = logging.getLogger("uvicorn.info")
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@glasfloss.get(
    "/model-lookup",
    response_model=FilterBuilt,
    response_model_exclude_none=True,
)
def parse_model_and_pricing(
    session: NewSession,
    token: Token,
    series: str,
    width: float,
    height: float,
    depth: float,
    exact: Optional[bool] = False,
    customer_id: int = 0,
) -> FilterBuilt:
    gate = token.permissions < auth.Permissions.sca_employee and customer_id
    if gate:
        try:
            (
                auth.VendorCustomerOperations(token, VendorCustomer, id="glasfloss")
                .allow_dev()
                .allow_customer("std")
                .get(session, {}, customer_id)
            )
        except:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
        else:
            pass

    try:
        filter_obj = Filter(width=width, height=height, depth=depth, exact=exact)
        type_ = ModelType[series.upper().strip()]
        return (
            FilterModel(session, type_, filter_obj)
            .calculate_pricing(customer_id)
            .to_obj()
        )
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
