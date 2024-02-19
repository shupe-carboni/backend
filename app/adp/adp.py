import typing
from fastapi import HTTPException, Depends
from starlette.background import BackgroundTask
from fastapi.responses import StreamingResponse 
from fastapi.routing import APIRouter
from typing import Literal
from app import auth
import app.adp.main as api
# from app.adp.models import ??

# TODO instead of just plain token authenication, use dependency injection to ensure that the user has
#       permissions for ADP specifically, and return the permission enum

adp = APIRouter(prefix='/adp', tags=['adp'])

class XLSXFileResponse(StreamingResponse):
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    def __init__(self, 
            content: typing.Any, 
            status_code: int = 200, 
            headers: typing.Optional[typing.Mapping[str, str]] = None, 
            media_type: typing.Optional[str] = None, 
            background: typing.Optional[BackgroundTask] = None, 
            filename: str = "download") -> None:
        super().__init__(content, status_code, headers, media_type, background)
        # NOTE escaped quotes are needed for filenames with spaces
        self.raw_headers.append((b"Content-Disposition",f"attachment; filename=\"{filename}.xlsx\"".encode('latin-1')))

@adp.get('/programs')
def all_programs():
    """list out all programs"""

@adp.get('/programs/{adp_customer_id}')
def customer_program(
        adp_customer_id: int,
        return_type: Literal['file', 'json'],
        stage: api.Stage='active',
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
        ) -> XLSXFileResponse:
    """Generate a program excel file and return for download or just the data in json format"""
    match token.permissions.get('adp'):
        case perm_level if isinstance(perm_level, auth.ADPPermPriority):
            print(perm_level.value)
            if return_type == 'file':
                file = api.generate_program(sca_customer_id=adp_customer_id, stage=stage.upper())
                return XLSXFileResponse(content=file.file_data, filename=file.file_name)

@adp.post('/programs/{adp_customer_id}')
def new_program(program_details: None):
    """add a new program for a customer"""

@adp.post('/programs/{adp_customer_id}/{program_id}')
def add_to_program(program_details: None):
    """add product to an existing program"""

@adp.patch('/programs/{adp_customer_id}/{program_id}')
def modify_program(program_details: None):
    """modify product listed on an existing program"""