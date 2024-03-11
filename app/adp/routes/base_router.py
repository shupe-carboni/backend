import logging
from typing import Optional, Mapping, Any, Annotated
from fastapi import HTTPException, Depends, status 
from starlette.background import BackgroundTask
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter

from app import auth, downloads
from app.db import Session, ADP_DB, Stage
from app.adp.main import generate_program
from app.adp.utils.programs import EmptyProgram
from app.adp.models import DownloadLink

adp = APIRouter(prefix='/adp', tags=['adp'])
logger = logging.getLogger('uvicorn.info')
ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_perms_present)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]

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


@adp.get('/programs/{adp_customer_id}/get-download', tags=['programs', 'file-download'])
def customer_program_get_dl(
        token: ADPPerm,
        adp_customer_id: int,
        stage: Stage,
    ) -> DownloadLink:
    """Generate one-time-use hash value for download"""
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        download_id = downloads.DownloadIDs.generate_id(customer_id=adp_customer_id, stage=Stage(stage))
        return DownloadLink(downloadLink=f'/adp/programs/{adp_customer_id}/download?download_id={download_id}')

    else:
        print("Enforce that the customer is allowed to have the program associated with the adp_customer_id selected")
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@adp.get('/programs/{adp_customer_id}/download', tags=['programs', 'file-download'], response_class=XLSXFileResponse)
def customer_program_dl_file(
        session: NewSession,
        adp_customer_id: int,
        download_id: str,
    ) -> XLSXFileResponse:
    """Generate a program excel file and return for download"""
    try:
        dl_obj = downloads.DownloadIDs.use_download(customer_id=adp_customer_id, id_value=download_id)
        file = generate_program(session=session, customer_id=adp_customer_id, stage=dl_obj.stage.name)
        return XLSXFileResponse(content=file.file_data, filename=file.file_name)
    except EmptyProgram:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="The file requested does not contain any data")
    except (downloads.NonExistant, downloads.Expired):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Download has either been used, expired, or is not valid')
    except downloads.CustomerIDNotMatch:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Customer ID does not match the id registered with this link')
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

