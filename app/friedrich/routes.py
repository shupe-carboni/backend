import logging
from os import getenv
from typing import Annotated
from enum import StrEnum, auto
import aiohttp
from fastapi import HTTPException, status, Depends, Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from hashlib import sha256
from app.friedrich.requests import Login, GetQuotes
from app.friedrich.models import Quote
from app import auth

load_dotenv()

from app.db import DB_V2


friedrich = APIRouter(prefix="/friedrich", tags=["friedrich"])
logger = logging.getLogger("uvicorn.info")

NewSession = Annotated[Session, Depends(DB_V2.get_db)]
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]


async def initialize_cookies() -> None:
    async with aiohttp.ClientSession() as req_session:
        await Login(req_session).make_request()
        logger.info("Retrieved Friedrich Session Cookies")


class SyncStatus(StrEnum):
    NOT_RUN = auto()
    IN_PROGRESS = auto()
    COMPLETE = auto()
    FAILED = auto()


class SyncStatusState:
    current_state = SyncStatus.NOT_RUN

    @classmethod
    def update(cls, new_status: SyncStatus):
        cls.current_state = new_status


@friedrich.get("/sync/status")
def check_friedrich_quote_sync_status():
    return {"run_status": SyncStatusState.current_state}


@friedrich.post("/sync/local/quotes")
async def update_friedrich_quotes_from_quote_portal(
    session: NewSession, token: Token
) -> list[Quote]:
    """
    Make requests to the Friedrich Portal to
        - load all quotes and check the ones we have records for
        - view quotes individually
            - capture customer & project info
            - load line items
            - compare project details and line items to current state in DB
            - make updates to the DB as needed
    """
    try:
        SyncStatusState.update(SyncStatus.IN_PROGRESS)
        async with aiohttp.ClientSession() as req_session:
            quotes: GetQuotes = await GetQuotes(req_session=req_session).make_request()
            await quotes.format_resp().collect_addnl_details()
    except Exception as e:
        SyncStatusState.update(SyncStatus.FAILED)
        raise e
    else:
        SyncStatusState.update(SyncStatus.COMPLETE)
        return quotes.ret()


@friedrich.post("/sync/remote/quotes")
def create_new_friedrich_quotes(session: NewSession, token: Token) -> None:
    not_imp = (
        "Syncing locally created quotes with the quote portal"
        " is currently not supported.\n"
    )
    return Response(status_code=status.HTTP_501_NOT_IMPLEMENTED, content=not_imp)


@friedrich.get("/cross-reference")
def cross_reference_competitor_product(session: NewSession, competitor_model: str):
    """public endpoint to supply a friedrich part number in response
    to a request with a competitor part number

    NOTE setting the precedent here that cross references are in product attrs
        and the attr name is formatted "cross_ref_{BRAND}
    TODO provide more flexible search functionality
    """
    sql = """
        SELECT vp.vendor_product_identifier
        FROM vendor_products vp
        WHERE EXISTS (
            SELECT 1
            FROM vendor_product_attrs a
            WHERE a.vendor_product_id = vp.id
            AND attr LIKE 'cross_ref_%'
            AND value = :competitor_model
        )
        AND vp.vendor_id = 'friedrich';
    """
    result = DB_V2.execute(
        session, sql, params=dict(competitor_model=competitor_model)
    ).scalar_one_or_none()
    return {"model_number": result}
