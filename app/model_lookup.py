import logging
from typing import Annotated, Optional
from pydantic import BaseModel
from pydantic_core import ValidationError
from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends, status, Request

from app import auth
from app.db import Session, DB_V2
from app.adp.models import ProgAttrs
from app.glasfloss.parsing import (
    FilterBuilt,
    Filter,
    ModelType,
    FilterModel,
    disect_model,
)
from app.v2.models import VendorCustomer
from app.adp.extraction.models import parse_model_string
from app.adp.utils.models import ParsingModes
from app.admin.models import VendorId, ModelLookupADP, ModelLookupGlasfloss


model_lookup = APIRouter(
    prefix=f"/model-lookup", tags=["model number parsing and lookup"]
)
logger = logging.getLogger("uvicorn.info")
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


def extract_query_params(model: BaseModel, request: Request) -> dict:
    try:
        params = model(**request.query_params).model_dump()
    except ValidationError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
    else:
        return params


@model_lookup.get("/{vendor_id}")
def parse_model_and_pricing(
    session: NewSession, token: Token, vendor_id: VendorId, request: Request
):
    """dynamically provide model parsing service for vendors with custom product"""
    match vendor_id:
        case VendorId.ADP:
            params = extract_query_params(ModelLookupADP, request)
            return adp_parse_full_model_number(session, token, **params).model_dump(
                exclude_none=True
            )
        case VendorId.GLASFLOSS:
            params = extract_query_params(ModelLookupGlasfloss, request)
            return glasfloss_parse_model(session, token, **params).model_dump(
                exclude_none=True
            )


def adp_parse_full_model_number(
    session: Session,
    token: Token,
    model_number: str,
    customer_id: int = 0,
    future: bool = False,
) -> ProgAttrs:
    """Used for feature extraction parsed from the model number and price check
    based on the permissions.

    if adp_customer_id is 0 AND permitted as an sca employee or above,
    base price is calculated and shown, alternatively if an id is given,
    that customer's pricing is calculated

    if the requester is permitted under a customer type,
    a check is done to see if the customer is associated with the adp_customer_id
    provided in the request.

    """
    adp_perm = token.permissions
    if adp_perm >= auth.Permissions.sca_employee:
        if not customer_id and future:
            parse_mode = ParsingModes.BASE_PRICE_FUTURE
        elif not customer_id and not future:
            parse_mode = ParsingModes.BASE_PRICE
        elif future:
            parse_mode = ParsingModes.CUSTOMER_PRICING_FUTURE
        else:
            parse_mode = ParsingModes.CUSTOMER_PRICING
    elif customer_id:
        try:
            (
                auth.VendorCustomerOperations(token, VendorCustomer, id="adp")
                .allow_dev()
                .allow_customer("std")
                .get(session, obj_id=customer_id)
            )
        except HTTPException as e:
            if e.status_code < 500:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail="Requested Customer pricing is not associated with the user",
                )
            else:
                raise e
        else:
            if adp_perm == auth.Permissions.developer:
                parse_mode = ParsingModes.DEVELOPER
            elif adp_perm >= auth.Permissions.customer_manager:
                parse_mode = ParsingModes.CUSTOMER_PRICING
            elif adp_perm >= auth.Permissions.customer_std:
                parse_mode = ParsingModes.ATTRS_ONLY
            else:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return ProgAttrs(
        **parse_model_string(session, customer_id, model_number, parse_mode)
        .dropna()
        .to_dict()
    )


def glasfloss_parse_model(
    session: NewSession,
    token: Token,
    series: str,
    width: float,
    height: float,
    depth: float,
    exact: Optional[bool] = False,
    model_number: Optional[str] = "",
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
        if not model_number:
            filter_obj = Filter(width=width, height=height, depth=depth, exact=exact)
            type_ = ModelType[series.upper().strip()]
            return (
                FilterModel(session, type_, filter_obj)
                .calculate_pricing(customer_id)
                .to_obj()
            )
        else:
            if any((series, width, height, depth)):
                logger.warning("model attribute parameters ignored")
            return (
                disect_model(session, model_number)
                .calculate_pricing(customer_id)
                .to_obj()
            )
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
