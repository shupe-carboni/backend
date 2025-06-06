"""
Places are typicially in the context of a relationship with another resource.
So, the only purpose of a resource dedicated to places is to get a list of places
in something like a location-picker. Relationships between places and customers
or places and quotes ought not be returned from here.

Only the admins can make modifications.
"""

from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from app import auth
from app.db import DB_V2
from app.places.models import ListOfPlaces, Place
from app.jsonapi.sqla_models import SCAPlace

API_TYPE = SCAPlace.__jsonapi_type_override__
places = APIRouter(prefix=f"/{API_TYPE}", tags=["places"])
Perm = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]


@places.get("")
async def all_places(
    session: NewSession,
    token: Perm,
    filter_name: str = None,
    filter_state: str = None,
) -> ListOfPlaces:
    """Places should be generally accessible.
    So long as someone has a valid auth token, they ought to be able to query this route
    """
    query = select(
        SCAPlace.id, SCAPlace.name, SCAPlace.state, SCAPlace.lat, SCAPlace.long
    )
    if filter_name or filter_state:
        query = query.where(
            and_(
                SCAPlace.name.like(f'%{filter_name.upper() if filter_name else ""}%'),
                SCAPlace.state.like(
                    f'%{filter_state.upper() if filter_state else ""}%'
                ),
            )
        )
    query = query.order_by(SCAPlace.name)
    records = session.execute(query).mappings()
    return ListOfPlaces(data=[Place(**record) for record in records])


@places.post("")
async def new_place(
    session: NewSession,
    token: Perm,
) -> None:
    raise HTTPException(status_code=501)


@places.patch("/{place_id}")
async def mod_place(
    session: NewSession,
    token: Perm,
) -> None:
    raise HTTPException(status_code=501)


@places.delete("/{place_id}")
async def remove_place(
    session: NewSession,
    token: Perm,
) -> None:
    raise HTTPException(status_code=501)
