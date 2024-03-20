from typing import Annotated
from fastapi import HTTPException, Depends, status, UploadFile
from fastapi.routing import APIRouter
from pandas import read_csv, read_excel
from numpy import nan

from app import auth
from app.db import Session, ADP_DB
from app.adp.main import add_ratings_to_program
from app.adp.models import (
    RatingsResp,
    RatingsQuery,
    Rating,
    Ratings
)
from app.jsonapi.sqla_models import serializer, ADPProgramRating

ADP_RATINGS_RESOURCE = ADPProgramRating.__jsonapi_type_override__
ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_perms_present)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]

prog_ratings = APIRouter(prefix=f'/{ADP_RATINGS_RESOURCE}', tags=['ratings','programs'])

@prog_ratings.get('', tags=['jsonapi'])
async def get_all_ratings_on_programs(
        token: ADPPerm,
        session: NewSession,
        query: RatingsQuery=Depends()
    ) -> RatingsResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@prog_ratings.get('/{rating_id}', tags=['jsonapi'])
async def get_a_specific_rating(
        token: ADPPerm,
        adp_customer_id: int,
        session: NewSession,
        query: RatingsQuery=Depends()
    ) -> RatingsResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@prog_ratings.post('/{adp_customer_id}', tags=['file-upload'])
async def add_program_ratings(
        token: ADPPerm,
        ratings_file: UploadFile,
        adp_customer_id: int,
        session: NewSession
    ) -> None:
    """add ratings to a customer's profile"""
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

    raise HTTPException(status.HTTP_401_UNAUTHORIZED)