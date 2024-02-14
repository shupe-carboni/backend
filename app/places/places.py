from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth
from app.places.models import PlaceQuery, PlaceResponse

places = APIRouter(prefix='/places', tags=['places'])

@places.get('')
async def places_collection(
        query: PlaceQuery=Depends(), # type: ignore
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> PlaceResponse:
    raise HTTPException(status_code=501)