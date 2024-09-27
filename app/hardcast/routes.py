import logging
import traceback
from typing import Annotated
from fastapi import HTTPException, status, Depends, UploadFile
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.hardcast import confirmations
from app import auth
from app.db import DB_V2, File

hardcast = APIRouter(prefix="/hardcast", tags=["hardcast"])
logger = logging.getLogger("uvicorn.info")
Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@hardcast.post("/confirmations")
async def new_confirmation(
    session: NewSession,
    token: Token,
    file: UploadFile,
) -> JSONResponse:
    if token.permissions != auth.Permissions.hardcast_confirmations:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    new_conf = File(file.filename, file.content_type, await file.read())
    try:
        confirmation = confirmations.extract_from_file(new_conf.file_content)
    except Exception:
        tb = traceback.format_exc()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=tb)
    else:
        confirmations.save_record(session, confirmation)
        return JSONResponse(confirmations.asdict(confirmation))
