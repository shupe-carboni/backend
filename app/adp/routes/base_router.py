import logging
from typing import Annotated
from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends, status, UploadFile, Response
from pandas import read_csv, read_excel
from numpy import nan

from app import auth, downloads
from app.db import Session, ADP_DB, Stage
from app.adp.models import ProgAttrs
from app.v2.models import VendorCustomer
from app.adp.utils.programs import EmptyProgram
from app.adp.extraction.models import parse_model_string
from app.adp.utils.models import ParsingModes
from app.adp.utils.workbook_factory import generate_program
from app.downloads import DownloadLink, XLSXFileResponse
from app.adp.extraction.ratings import add_ratings_to_program
from app.adp.models import Rating, Ratings


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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

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
        return file


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


@adp.post("/adp-program-ratings/{vendor_customer_id}", tags=["file-upload", "ratings"])
async def add_program_ratings(
    token: Token, ratings_file: UploadFile, vendor_customer_id: int, session: NewSession
) -> None:
    """add ratings to a customer's profile"""
    if token.permissions >= auth.Permissions.sca_employee:
        ratings_data = await ratings_file.read()
        match ratings_file.content_type:
            case "text/csv":
                ratings_df = read_csv(ratings_data).replace({nan: None})
            case "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                ratings_df = read_excel(ratings_data).replace({nan: None})
            case _:
                raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        ratings = Ratings(
            ratings=[Rating(**row._asdict()) for row in ratings_df.itertuples()]
        )
        try:
            add_ratings_to_program(
                session=session, adp_customer_id=vendor_customer_id, ratings=ratings
            )
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status_code=status.HTTP_202_ACCEPTED)
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)
