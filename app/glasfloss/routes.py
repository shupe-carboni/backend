import logging
from typing import Annotated
from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends, status

from app import auth
from app.db import Session, DB_V2
from app.v2.models import VendorCustomer
from app.glasfloss.parsing import FilterModel, Filter, ModelType

glasfloss = APIRouter(prefix=f"/glasfloss", tags=["glasfloss"])
logger = logging.getLogger("uvicorn.info")
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@glasfloss.get(
    "/model-lookup",
    response_model=None,
    response_model_exclude_none=True,
)
def parse_model_and_pricing(
    session: NewSession,
    token: Token,
    series: str,
    width: float,
    height: float,
    depth: float,
    exact: bool,
    customer_id: int = 0,
) -> None:
    filter_obj = Filter(width=width, height=height, depth=depth, exact=exact)
    type_ = ModelType[series.upper().strip()]
    try:
        return FilterModel(type_, filter_obj).to_dict()
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
