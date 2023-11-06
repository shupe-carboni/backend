from fastapi import APIRouter, Depends, HTTPException
from app import auth

relationships = APIRouter()

@relationships.get("/{primary}/{id_}/{secondary}", tags=["relationships"])
def get_related_handler(
        primary: str,
        id_: int,
        secondary: str,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ):
    return HTTPException(status_code=501)

@relationships.get("/{primary}/{id_}/relationships/{secondary}", tags=["relationships"])
def get_self_relationship_handler(
        primary: str,
        id_: int,
        secondary: str,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ):
    return HTTPException(status_code=501)