from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app import auth
from app.db import SCA_DB
from app.places.models import PlaceQuery, PlaceResponse, PlaceQueryJSONAPI
from app.jsonapi.sqla_models import SCAPlace

API_TYPE = SCAPlace.__jsonapi_type_override__
places = APIRouter(prefix=f'/{API_TYPE}', tags=['places', 'jsonapi'])
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]

def convert_query(query: PlaceQuery) -> PlaceQueryJSONAPI:
    return PlaceQueryJSONAPI(**query.model_dump(exclude_none=True)).model_dump(by_alias=True, exclude_none=True)

@places.get('')
async def places_collection(
        query: PlaceQuery=Depends(),
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> PlaceResponse:
    raise HTTPException(status_code=501)