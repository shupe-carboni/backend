import logging
from typing import Annotated
from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends, status

from app import auth, downloads
from app.db import Session, ADP_DB, Stage
from app.adp.models import ProgAttrs
from app.jsonapi.sqla_models import ADPCustomer
from app.v2.models import VendorCustomer
from app.adp.utils.programs import EmptyProgram
from app.adp.extraction.models import parse_model_string
from app.adp.utils.models import ParsingModes
from app.adp.utils.workbook_factory import generate_program
from app.downloads import DownloadLink, XLSXFileResponse

adp = APIRouter(prefix=f"/adp", tags=["adp"])
logger = logging.getLogger("uvicorn.info")
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]


def generate_dl_link(adp_customer_id: int, download_id: int) -> DownloadLink:
    link = DownloadLink(
        downloadLink=f"/vendors/adp/programs/{adp_customer_id}"
        f"/download?download_id={download_id}"
    )
    return link


@adp.post("/programs/{adp_customer_id}/download", tags=["programs", "file-download"])
def customer_program_get_dl(
    token: Token,
    session: NewSession,
    adp_customer_id: int,
    stage: Stage,
) -> DownloadLink:
    """Generate one-time-use hash value for download"""
    if token.permissions < auth.Permissions.sca_employee:
        try:
            auth.ADPOperations(token, ADPCustomer).allow_dev().allow_customer(
                "std"
            ).get(session=session, obj_id=adp_customer_id)
        except HTTPException as e:
            if e.status_code == 204:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            else:
                raise e

    download_id = downloads.DownloadIDs.add_request(
        resource=f"vendors/adp/programs/{adp_customer_id}/download", stage=Stage(stage)
    )
    return generate_dl_link(adp_customer_id, download_id)


@adp.get(
    "/programs/{adp_customer_id}/download",
    tags=["programs", "file-download"],
    response_class=XLSXFileResponse,
)
def customer_program_dl_file(
    session: NewSession,
    adp_customer_id: int,
    download_id: str,
) -> XLSXFileResponse:
    """Generate a program excel file and return for download"""
    dl_obj = downloads.DownloadIDs.use_download(
        resource=f"vendors/adp/programs/{adp_customer_id}/download",
        id_value=download_id,
    )
    try:
        file = generate_program(
            session=session, customer_id=adp_customer_id, stage=dl_obj.stage
        )
    except EmptyProgram:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="The file requested does not contain any data",
        )
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    else:
        return XLSXFileResponse(content=file.file_data, filename=file.file_name)


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
    price_year: int = 2025,
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
        if not customer_id:
            parse_mode = ParsingModes.BASE_PRICE
        else:
            if price_year == 2025:
                parse_mode = ParsingModes.CUSTOMER_PRICING
            elif price_year == 2024:
                parse_mode = ParsingModes.CUSTOMER_PRICING_2024
    elif customer_id:
        try:
            (
                auth.VendorCustomerOperations(token, VendorCustomer, vendor_id="adp")
                .allow_dev()
                .allow_customer("std")
                .get(session, obj=customer_id)
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
                if price_year == 2025:
                    parse_mode = ParsingModes.CUSTOMER_PRICING
                elif price_year == 2024:
                    parse_mode = ParsingModes.CUSTOMER_PRICING_2024
            elif adp_perm >= auth.Permissions.customer_std:
                parse_mode = ParsingModes.ATTRS_ONLY
            else:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return parse_model_string(session, customer_id, model_num, parse_mode)
