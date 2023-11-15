"""Catch-all for undocumented links"""
from fastapi import APIRouter, Depends, HTTPException
from app.jsonapi import JSONAPIResourceObject
from app import auth

relationships = APIRouter()

@relationships.get("/{primary}/{id_}/{secondary}", tags=["relationships"])
def get_related_handler(
        primary: str,
        id_: int,
        secondary: str,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> JSONAPIResourceObject:
    """Returns a collection of resource objects representing the secondary resource
        similar to GET /secondary filtering for the primary resource id_"""
    raise HTTPException(status_code=501)

@relationships.get("/{primary}/{id_}/relationships/{secondary}", tags=["relationships"])
def get_self_relationship_handler(
        primary: str,
        id_: int,
        secondary: str,
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ):
    """Returns a list of Resource Identifiers: { "type": type, "id": id } related to id_
        where the type is the seconady resource"""
    raise HTTPException(status_code=501)