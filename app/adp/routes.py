from dotenv import load_dotenv; load_dotenv()
from dataclasses import dataclass
from os import getenv
from datetime import datetime, timedelta
from typing import Literal, Optional, Mapping, Any, Annotated
from fastapi import HTTPException, Depends, status, UploadFile, BackgroundTasks, Response
from starlette.background import BackgroundTask
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter
from pandas import read_excel, read_csv
from numpy import nan
import logging
from uuid import uuid4, UUID  # uuid4 is for random generation

from app import auth
from app.db import Session, ADP_DB, Stage
from app.adp.main import (
    generate_program, add_model_to_program,
    add_parts_to_program, add_ratings_to_program,
    update_ratings_reference,
    update_all_unregistered_program_ratings
)
from app.adp.utils.programs import EmptyProgram
from app.adp.models import CoilProgQuery, CoilProgResp, NewCoilRObj, NewAHRObj, Rating, Ratings

class NonExistant(Exception):...
class Expired(Exception):...
class CustomerIDNotMatch(Exception):...

@dataclass
class DownloadRequest:
    customer_id: int
    stage: Stage
    download_id: UUID
    expires_at: float

    def __hash__(self) -> int:
        return self.download_id.__hash__()
    
    def expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    def __eq__(self, other) -> bool:
        return self.download_id == other

class DownloadIDs:
    active_requests: set[DownloadRequest] = set()

    @classmethod
    def generate_id(cls, customer_id: int, stage: Stage) -> str:
        value = uuid4()
        expiry = datetime.now() + timedelta(float(getenv('DL_LINK_DURATION'))*60)
        request = DownloadRequest(
            customer_id=customer_id,
            stage=stage,
            download_id=value,
            expires_at=expiry
        )
        cls.active_requests.add(request)
        return str(request.download_id)
    
    @classmethod
    def use_download(cls, customer_id: int, id_value: str) -> DownloadRequest:
        incoming_uuid: UUID = UUID(id_value)
        for stored_request in cls.active_requests:
            if stored_request == incoming_uuid:
                if stored_request.customer_id == customer_id:
                    if not stored_request.expired():
                        cls.active_requests.remove(stored_request)
                        return stored_request
                    else:
                        raise Expired
                else:
                    raise CustomerIDNotMatch
        raise NonExistant
            



adp = APIRouter(prefix='/adp', tags=['adp'])
logger = logging.getLogger('uvicorn.info')
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
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]

@adp.get('/programs', tags=['jsonapi', 'programs'])
def all_programs(
        token: ADPPerm,
        query: CoilProgQuery,   # type: ignore
        session: NewSession
    ):
    """list out all programs"""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@adp.get('/update-ratings-reference', tags=['private'])
def update_ratings_ref(
        token: ADPPerm,
        session: NewSession,
        bg: BackgroundTasks
    ):
    """Update the rating reference table in the background
        Due to the size of the table being downloaded, this
        is a long-running task"""
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        logger.info('Update request received for ADP Ratings Reference Table. Sending to background')
        bg.add_task(update_ratings_reference, session=session)
        return Response(status_code=status.HTTP_202_ACCEPTED)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@adp.get('/update-unregistered-ratings', tags=['private'])
def update_unregistered_ratings(
        token: ADPPerm,
        session: NewSession,
        bg: BackgroundTasks
    ):
    """Update all program ratings that haven't been found in the ratings reference"""
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        logger.info('Update Request Received for ADP Program Ratings. Sending to background')
        bg.add_task(update_all_unregistered_program_ratings, session=session)
        return Response(status_code=status.HTTP_202_ACCEPTED)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@adp.get('/{adp_customer_id}/program', tags=['jsonapi', 'programs'])
def customer_program(
        session: NewSession,
        token: ADPPerm,
        adp_customer_id: int,
        stage: Stage='active',
    ) -> CoilProgResp:
    """Generate a program excel file and return for download or just the data in json format"""
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        print("allowed")
    else:
        print("Enforce that the customer is allowed to have the program associated with the adp_customer_id selected")
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@adp.get('/{adp_customer_id}/program/get-download', tags=['programs'])
def customer_program(
        token: ADPPerm,
        adp_customer_id: int,
        stage: Stage,
    ):
    """Generate one-time-use hash value for download"""
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        download_id = DownloadIDs.generate_id(customer_id=adp_customer_id, stage=Stage(stage))
        return {'downloadLink': f'/adp/{adp_customer_id}/program/download?download_id={download_id}'}

    else:
        print("Enforce that the customer is allowed to have the program associated with the adp_customer_id selected")
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@adp.get('/{adp_customer_id}/program/download', tags=['programs'])
def customer_program(
        session: NewSession,
        adp_customer_id: int,
        download_id: str,
    ) -> XLSXFileResponse:
    """Generate a program excel file and return for download"""
    try:
        dl_obj = DownloadIDs.use_download(customer_id=adp_customer_id, id_value=download_id)
        file = generate_program(session=session, customer_id=adp_customer_id, stage=dl_obj.stage.name)
        return XLSXFileResponse(content=file.file_data, filename=file.file_name)
    except EmptyProgram:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="The file requested does not contain any data")
    except (NonExistant, Expired):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Download has either been used, expired, or is not valid')
    except CustomerIDNotMatch:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Customer ID does not match the id registered with this link')
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@adp.post('/{adp_customer_id}/program/coils', tags=['jsonapi', 'programs'])
def add_to_coil_program(
        token: ADPPerm,
        session: NewSession,
        adp_customer_id: int,
        new_coil: NewCoilRObj,
        ):
    """add coil product for a customer"""
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        model_num = new_coil.attributes.model_number
        new_id = add_model_to_program(session=session, model=model_num, adp_customer_id=adp_customer_id)
        return {"new id": new_id}
    else:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@adp.post('/{adp_customer_id}/program/air-handlers', tags=['jsonapi', 'programs'])
def add_to_ah_program(
        token: ADPPerm,
        session: NewSession,
        adp_customer_id: int,
        new_ah: NewAHRObj,
    ):
    """modify product listed on an existing program"""
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        model_num = new_ah.attributes.model_number
        new_id = add_model_to_program(session=session, model=model_num, adp_customer_id=adp_customer_id)
        return {"new id": new_id}
    else:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@adp.get('/{adp_customer_id}/program/ratings', tags=['jsonapi','ratings'])
async def get_program_ratings(
        token: ADPPerm,
        adp_customer_id: int,
        session: NewSession
    ):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@adp.post('/{adp_customer_id}/program/ratings', tags=['ratings'])
async def add_program_ratings(
        token: ADPPerm,
        ratings_file: UploadFile,
        adp_customer_id: int,
        session: NewSession
    ):
    """add ratings to a customer's program"""
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        ratings_data = await ratings_file.read()
        match ratings_file.content_type:
            case 'text/csv':
                ratings_df = read_csv(ratings_data).replace({nan: None})
            case 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                ratings_df = read_excel(ratings_data).replace({nan: None})
            case _:
                raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        ratings = Ratings(ratings=[Rating(**row._asdict()) for row in ratings_df.itertuples()])
        add_ratings_to_program(session=session, adp_customer_id=adp_customer_id, ratings=ratings)

    else:
        print("Enforce that the customer is allowed to add ratings to the adp_customer_id selected")
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@adp.post('/{adp_customer_id}/program/parts', tags=['parts'])
async def add_program_parts(
        token: ADPPerm,
        parts: list[str],
        adp_customer_id: int,
        session: NewSession
    ):
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        try:
            add_parts_to_program(session=session, adp_customer_id=adp_customer_id, part_nums=parts)
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))