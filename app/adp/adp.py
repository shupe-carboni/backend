from typing import Literal, Optional, Mapping, Any, Annotated
from fastapi import HTTPException, Depends, status
from starlette.background import BackgroundTask
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter

from app import auth
import app.adp.main as api
from app.adp.models import CoilProgQuery, CoilProgResp

adp = APIRouter(prefix='/adp', tags=['adp'])

class XLSXFileResponse(StreamingResponse):
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    def __init__(self, 
            content: Any, 
            status_code: int = 200, 
            headers: Optional[Mapping[str, str]] = None, 
            media_type: Optional[str] = None, 
            background: Optional[BackgroundTask] = None, 
            filename: str = "download") -> None:
        super().__init__(content, status_code, headers, media_type, background)
        # NOTE escaped quotes are needed for filenames with spaces
        self.raw_headers.append((b"Content-Disposition",f"attachment; filename=\"{filename}.xlsx\"".encode('latin-1')))

ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_perms_present)]

@adp.get('/programs')
def all_programs(
        token: ADPPerm,
        query: CoilProgQuery,   # type: ignore
    ):
    """list out all programs"""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@adp.get('/{adp_customer_id}/program')
def customer_program(
        token: ADPPerm,
        adp_customer_id: int,
        return_type: Literal['file', 'json'],
        stage: api.Stage='active',
    ) -> CoilProgResp:
    """Generate a program excel file and return for download or just the data in json format"""
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        if return_type == 'file':
            stage_str = stage.upper()
            file = api.generate_program(customer_id=adp_customer_id, stage=stage_str)
            return XLSXFileResponse(content=file.file_data, filename=file.file_name)
    else:
        print("Enforce that the customer is allowed to have the program associated with the adp_customer_id selected")
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@adp.post('{adp_customer_id}/program/coils')
def add_to_coil_program(
        token: ADPPerm,
        program_details: None,
        ):
    """add coil product for a customer"""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@adp.post('{adp_customer_id}/program/air-handlers')
def add_to_ah_program(
        token: ADPPerm,
        program_details: None,
    ):
    """modify product listed on an existing program"""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)