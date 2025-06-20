"""
* Ajax_ValidateSignOn.aspx -- authentication
    * if the cookie is stored and still valid, potentially avoidable for most syncs
* Ajax_DashboardV2_LoadQuotes.aspx -- list of quotes
* CreateNewQuote.aspx -- quote project details by quote id
* Ajax_CreateQuoteManageLineItems.aspx -- quote line items

Capturing data will require various combinations of query parameters in GET requests
and parsing of HTML responses to the simulated AJAX calls
"""

import logging
from os import getenv
from typing import Annotated
import requests
from fastapi import HTTPException, status, Depends, Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from hashlib import sha256
from random import randint
from bs4 import BeautifulSoup as bs

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


class Action:

    def __init__(self) -> None:
        self.domain: str = getenv("FRIEDRICH_QUOTE_PORTAL_DOMAIN")
        self.contact_id: str = getenv("FRIEDRICH_CONTACT_ID")
        self.path: str
        self.params: dict[str, str | int]

    def _set_cache(self) -> int:
        return randint(0, 99999)

    def __str__(self) -> str:
        """build the url with parameters"""
        params = self.params
        params["Cache"] = self._set_cache()
        endpoint = self.domain + self.path
        return f"{endpoint}?{'&'.join([f'{k}={v}' for k,v in params.items()])}"


class Login(Action):
    def __init__(self) -> None:
        super().__init__()
        self.path: str = "Ajax_ValidateSignOn.aspx"
        self.params = {
            "EmailAddress": getenv("FRIEDRICH_LOGIN_NAME"),
            "Password": getenv("FRIEDRICH_LOGIN_PASSWORD"),
        }


class GetQuotes(Action):
    def __init__(self) -> None:
        super().__init__()
        self.path: str = "Ajax_DashboardV2_LoadQuotes.aspx"
        self.params = {"ContactID": self.contact_id}


Cookies = dict[str, str]
__cookies: Cookies = dict()


def cookies(new_cookies: Cookies = None) -> Cookies:
    global __cookies
    if new_cookies:
        __cookies = new_cookies
    return __cookies


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
        # for cookie in cookies():
        #     req_session.cookies.set(**cookie)
        get_quotes = GetQuotes()
        quotes = bs(req_session.get(url=str(get_quotes)).text)

    return Response(content=quotes.prettify(), status_code=status.HTTP_200_OK)


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
