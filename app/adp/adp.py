import typing
from fastapi import HTTPException, Depends, status
from starlette.background import BackgroundTask
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter
from typing import Literal
from app import auth
import app.adp.main as api
from app.adp.models import CoilProgQuery, CoilProgResp

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

def adp_perms_present(token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)) -> auth.VerifiedToken:
    """chained dependency on authentication enforcing that the auth token
        contains defined permissions for use of the ADP resource"""
    if token.perm_level('adp') < 0:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail='Permissions for accesss to ADP have not been defined.'
        )
    return token

ADPPerm = typing.Annotated[auth.VerifiedToken, Depends(adp_perms_present)]

@adp.get('/programs')
def all_programs(
        token: ADPPerm,
        query: CoilProgQuery,   # type: ignore
    ):
    """list out all programs"""

@adp.get('{adp_customer_id}/programs')
def customer_program(
        token: ADPPerm,
        adp_customer_id: int,
        return_type: Literal['file', 'json'],
        stage: api.Stage='active',
    ) -> CoilProgResp:
    """Generate a program excel file and return for download or just the data in json format"""
    print(token.perm_level('adp'))
    if return_type == 'file':
        file = api.generate_program(sca_customer_id=adp_customer_id, stage=stage.upper())
        return XLSXFileResponse(content=file.file_data, filename=file.file_name)

@adp.post('{adp_customer_id}/program/coils')
def add_to_coil_program(
        token: ADPPerm,
        program_details: None,
        ):
    """add coil product for a customer"""

@adp.post('{adp_customer_id}/program/air-handlers')
def add_to_ah_program(
        token: ADPPerm,
        program_details: None,
    ):
    """modify product listed on an existing program"""