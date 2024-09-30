import logging
import traceback
from io import BytesIO
from base64 import b64decode
from typing import Annotated, Optional
from fastapi import HTTPException, status, Depends, Header
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.hardcast import confirmations
from app import auth
from app.db import DB_V2

hardcast = APIRouter(prefix="/hardcast", tags=["hardcast"])
logger = logging.getLogger("uvicorn.info")
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


class NewFile(BaseModel):
    file: str
    content_type: str


@hardcast.post("/confirmations")
async def new_confirmation(
    session: NewSession,
    # token: Token,
    file: NewFile,
    authorization: Optional[str] = Header(None),
) -> JSONResponse:
    # if token.permissions != auth.Permissions.hardcast_confirmations:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if authorization:
        warn_msg = (
            "Endpoint unprotected but an auth header was sent, "
            f"starting with {authorization[:30]}"
        )
    else:
        warn_msg = "Endpoint unprotected and no auth header was sent."

    if file.content_type != "application/pdf":
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    logger.warning(warn_msg)
    data = b64decode(file.file)
    new_conf = BytesIO(data)
    try:
        confirmation = confirmations.extract_from_file(new_conf)
    except Exception:
        tb = traceback.format_exc()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=tb)
    else:
        confirmations.save_record(session, confirmation)
        return JSONResponse(confirmations.asdict(confirmation))
