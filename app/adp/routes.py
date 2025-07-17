import logging
from typing import Annotated
from fastapi import Depends, status, Response
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, DB_V2
from app.adp.models import RatingExpanded, RatingsExpanded

ratings = APIRouter(prefix="/adp/ratings", tags=["adp", "admin", "ratings"])
logger = logging.getLogger("uvicorn.info")
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@ratings.get("/{customer_id}")
def ratings_collection(
    token: Token, session: NewSession, customer_id: int
) -> RatingsExpanded:
    sql = """
       SELECT *
       FROM adp_program_ratings
       WHERE customer_id = :customer_id
    """
    results = (
        DB_V2.execute(session, sql, dict(customer_id=customer_id)).mappings().fetchall()
    )
    if results:
        return RatingsExpanded(ratings=[RatingExpanded(**res) for res in results])
    return Response(status_code=status.HTTP_204_NO_CONTENT)
