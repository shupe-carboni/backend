import logging
import traceback
from os import getenv
from io import BytesIO
from base64 import b64decode
from typing import Annotated, Optional
from fastapi import HTTPException, status, Depends, Header, Request
from fastapi.routing import APIRouter
from starlette.templating import Jinja2Templates, _TemplateResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.hardcast import confirmations
from dotenv import load_dotenv

load_dotenv()

from app.db import DB_V2

hardcast = APIRouter(prefix="/hardcast", tags=["hardcast"])
logger = logging.getLogger("uvicorn.info")
NewSession = Annotated[Session, Depends(DB_V2.get_db)]
templates = Jinja2Templates("./app/hardcast/templates")
FLOW_NAME = getenv("FLOW_NAME")


class NewFile(BaseModel):
    file: str
    content_type: str


@hardcast.post("/confirmations")
async def new_confirmation(
    request: Request,
    session: NewSession,
    file: NewFile,
    x_ms_workflow_name: Annotated[Optional[str], Header()] = None,
) -> _TemplateResponse:
    if not x_ms_workflow_name or x_ms_workflow_name != FLOW_NAME:
        logger.warning("Request recieved with invalid or missing workflow name header.")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if file.content_type != "application/pdf":
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    data = b64decode(file.file)
    new_conf = BytesIO(data)
    try:
        confirmation = confirmations.extract_from_file(new_conf)
    except Exception:
        tb = traceback.format_exc()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=tb)
    else:
        try:
            variable_values = confirmations.analyze_confirmation(
                session, confirmation=confirmation
            )
        except confirmations.CityNotExtracted as e:
            error_msg = (
                "The city-part of the address was unable to be extracted "
                f"given the address: {e.address}"
            )
            logger.error(error_msg)
            detail = dict(exception_type="CityNotExtracted", error_msg=error_msg)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
        except Exception as e:
            tb = traceback.format_exc()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=tb)
        else:
            variable_values["request"] = request
            confirmations.save_record(session, confirmation)
            return templates.TemplateResponse(
                "confirmation_analysis_email.html", variable_values
            )
