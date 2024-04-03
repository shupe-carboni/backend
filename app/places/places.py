from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app import auth
from app.db import SCA_DB
from app.places.models import PlaceQuery, PlaceResponse, PlaceQueryJSONAPI
from app.jsonapi.sqla_models import SCAPlace
from app.jsonapi.core_models import convert_query

API_TYPE = SCAPlace.__jsonapi_type_override__
places = APIRouter(prefix=f'/{API_TYPE}', tags=['places', 'jsonapi'])
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(PlaceQueryJSONAPI)

@places.get('')
async def places_collection(
        query: PlaceQuery=Depends(),
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> PlaceResponse:
    raise HTTPException(status_code=501)