from typing import Annotated
from fastapi import HTTPException, Depends, status
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.adp.main import add_parts_to_program
from app.adp.models import (
    Parts,
)
from app.jsonapi.sqla_models import serializer, ADPProgramPart

ADP_PARTS_RESOURCE = ADPProgramPart.__jsonapi_type_override__
ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_perms_present)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]

prog_parts = APIRouter(prefix=f'/{ADP_PARTS_RESOURCE}', tags=['parts','programs'])

@prog_parts.post('/{adp_customer_id}', tags=['jsonapi'])
async def add_program_parts(
        token: ADPPerm,
        adp_customer_id: int,
        session: NewSession,
        parts: Parts=Depends(),
    ):
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        try:
            add_parts_to_program(session=session, adp_customer_id=adp_customer_id, part_nums=parts)
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))