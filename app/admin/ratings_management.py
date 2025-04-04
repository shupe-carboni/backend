import logging
from typing import Annotated
from concurrent.futures import ThreadPoolExecutor
from fastapi import (
    HTTPException,
    Depends,
    status,
    BackgroundTasks,
    Response,
    UploadFile,
)
from pandas import read_csv, read_excel
from numpy import nan
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.adp.models import Rating, Ratings
from app.adp.extraction.ratings import (
    update_ratings_reference,
    update_all_unregistered_program_ratings,
    add_ratings_to_program,
)

ratings_admin = APIRouter(prefix="/admin/adp", tags=["adp", "admin", "ratings"])
logger = logging.getLogger("uvicorn.info")
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]

executor = ThreadPoolExecutor(max_workers=2)


@ratings_admin.post("/update-ratings-reference")
def update_ratings_ref(
    token: Token,
    session: NewSession,
    # bg: BackgroundTasks
):
    """Update the rating reference table in the background
    Due to the size of the table being downloaded, this
    is a long-running task"""
    if token.permissions >= auth.Permissions.sca_admin:
        logger.info(
            "Update request received for ADP Ratings Reference Table. "
            "Sending to background"
        )
        executor.submit(update_ratings_reference, session=session)
        # bg.add_task(update_ratings_reference, session=session)
        return Response(status_code=status.HTTP_202_ACCEPTED)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@ratings_admin.post("/update-unregistered-ratings")
def update_unregistered_ratings(token: Token, session: NewSession, bg: BackgroundTasks):
    """Update all program ratings
    that haven't been found in the ratings reference"""
    if token.permissions >= auth.Permissions.sca_admin:
        logger.info(
            "Update Request Received for ADP Program Ratings. " "Sending to background"
        )
        bg.add_task(update_all_unregistered_program_ratings, session=session)
        return Response(status_code=status.HTTP_202_ACCEPTED)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@ratings_admin.post("/ratings/{vendor_customer_id}", tags=["file-upload", "ratings"])
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
