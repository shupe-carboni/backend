import logging
from typing import Annotated
from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends, status

from app import auth
from app.db import Session, ADP_DB
from app.adp.models import ProgAttrs
from app.v2.models import VendorCustomer
from app.adp.extraction.models import parse_model_string
from app.adp.utils.models import ParsingModes


adp = APIRouter(prefix=f"/adp", tags=["adp"])
logger = logging.getLogger("uvicorn.info")
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]


@adp.get(
    "/model-lookup",
    response_model=ProgAttrs,
    response_model_exclude_none=True,
)
def parse_model_and_pricing(
    session: NewSession,
    token: Token,
    model_num: str,
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
    return parse_model_string(session, customer_id, model_num, parse_mode)
