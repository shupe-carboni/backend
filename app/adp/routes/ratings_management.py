import logging
from typing import Annotated
from concurrent.futures import ThreadPoolExecutor
from fastapi import HTTPException, Depends, status, BackgroundTasks, Response
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.adp.extraction.ratings import (
    update_ratings_reference,
    update_all_unregistered_program_ratings,
)

ratings_admin = APIRouter(prefix="/admin", tags=["adp", "admin", "ratings"])
logger = logging.getLogger("uvicorn.info")
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]

executor = ThreadPoolExecutor(max_workers=2)


@ratings_admin.get("/update-ratings-reference")
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


@ratings_admin.get("/update-unregistered-ratings")
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
