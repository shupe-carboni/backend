from typing import Literal, Optional, Mapping, Any, Annotated
from fastapi import HTTPException, Depends, status, UploadFile
from starlette.background import BackgroundTask
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter
from pandas import read_excel, read_csv
from numpy import nan

from app import auth
from app.db import Session, ADP_DB, Stage
from app.adp.main import generate_program, add_model_to_program, add_parts_to_program, add_ratings_to_program
from app.adp.utils.programs import EmptyProgram
from app.adp.models import CoilProgQuery, CoilProgResp, NewCoilRObj, NewAHRObj, Rating, Ratings

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
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]

@adp.get('/programs')
def all_programs(
        token: ADPPerm,
        query: CoilProgQuery,   # type: ignore
        session: NewSession
    ):
    """list out all programs"""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@adp.get('/{adp_customer_id}/program')
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

@adp.get('/{adp_customer_id}/program/download')
def customer_program(
        session: NewSession,
        adp_customer_id: int,
        one_time_hash: str,
        stage: Stage='active',
    ) -> XLSXFileResponse:
    """Generate a program excel file and return for download"""
    if one_time_hash:
        stage_str = stage.upper()
        try:
            file = generate_program(session=session, customer_id=adp_customer_id, stage=stage_str)
            return XLSXFileResponse(content=file.file_data, filename=file.file_name)
        except EmptyProgram:
            raise HTTPException(status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    else:
        print("Enforce that the customer is allowed to have the program associated with the adp_customer_id selected")
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@adp.post('/{adp_customer_id}/program/coils')
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

@adp.post('/{adp_customer_id}/program/air-handlers')
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

@adp.post('/{adp_customer_id}/program/ratings')
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