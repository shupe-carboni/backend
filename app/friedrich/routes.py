import logging
from os import getenv
from typing import Annotated
import requests
from fastapi import HTTPException, status, Depends, Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from hashlib import sha256
from app.friedrich.models import *

load_dotenv()

from app.db import DB_V2


def validate_secret(secret: str) -> None:
    """not the best but it is the simplest"""
    if sha256(secret.encode("utf-8")).hexdigest() != SECRET:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)


friedrich = APIRouter(prefix="/friedrich", tags=["friedrich"])
logger = logging.getLogger("uvicorn.info")

NewSession = Annotated[Session, Depends(DB_V2.get_db)]

SECRET = sha256(getenv("FRIEDRICH_QUOTE_SYNC_SECRET").encode("utf-8")).hexdigest()
SecretValid = Annotated[None, Depends(validate_secret)]

# initialize cookies with a portal login
with requests.Session() as req_session:
    Login(req_session).make_request()
    logger.info("Retrieved Friedrich Session Cookies")


@friedrich.get("/sync/status")
def check_friedrich_quote_sync_status(): ...


@friedrich.patch("/sync/local/quotes")
def update_friedrich_quotes_from_quote_portal(
    session: NewSession, secret: SecretValid
) -> None:
    """
    Make requests to the Friedrich Portal to
        - load all quotes and check the ones we have records for
        - view quotes individually
            - capture customer & project info
            - load line items
            - compare project details and line items to current state in DB
            - make updates to the DB as needed
    """
    with requests.Session() as req_session:
        quotes = GetQuotes(req_session=req_session).make_request().format_resp()
        # return Response(content=None, status_code=status.HTTP_200_OK)
        return quotes


@friedrich.post("/sync/local/quotes")
def create_new_friedrich_quotes_from_quote_portal(
    session: NewSession, secret: SecretValid
) -> None:
    """
    Make requests to the Friedrich Portal to
    - load all quotes and check for ones we don't have
    - view quotes individually
        - capture customer & project info
        - load line items
        - register the quote details and products in our DB
    """
    return Response(status_code=status.HTTP_202_ACCEPTED)


@friedrich.patch("/sync/remote/quotes")
def update_friedrich_quotes_in_quote_portal(
    session: NewSession, secret: SecretValid
) -> None:
    not_imp = (
        "Syncing locally created quotes with the quote portal"
        " is currently not supported.\n"
    )
    return Response(status_code=status.HTTP_501_NOT_IMPLEMENTED, content=not_imp)


@friedrich.post("/sync/remote/quotes")
def create_new_friedrich_quotes(session: NewSession, secret: SecretValid) -> None:
    not_imp = (
        "Syncing locally created quotes with the quote portal"
        " is currently not supported.\n"
    )
    return Response(status_code=status.HTTP_501_NOT_IMPLEMENTED, content=not_imp)
