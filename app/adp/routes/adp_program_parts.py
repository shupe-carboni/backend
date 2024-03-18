from typing import Annotated
from fastapi import HTTPException, Depends, status
from fastapi.routing import APIRouter

from app import auth
from app.db import Session, ADP_DB
from app.adp.models import (
    NewPartRObj,
    PartsQuery,
    PartsResp
)
from app.jsonapi.sqla_models import serializer, ADPProgramPart

ADP_PARTS_RESOURCE = ADPProgramPart.__jsonapi_type_override__
ADPPerm = Annotated[auth.VerifiedToken, Depends(auth.adp_perms_present)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]

prog_parts = APIRouter(prefix=f'/{ADP_PARTS_RESOURCE}', tags=['parts','programs'])

@prog_parts.get(
        '',
        response_model=PartsResp,
        response_model_exclude_none=True,
        tags=['jsonapi']
)
def all_parts(
        token: ADPPerm,
        session: NewSession,
        query: PartsQuery=Depends()
    ) -> PartsResp:
    return auth.secured_get_query(
        db=ADP_DB,
        session=session,
        token=token,
        auth_scheme=auth.Permissions['adp'],
        resource=ADP_PARTS_RESOURCE,
        query=query
    )

async def add_parts_to_program(session: Session, adp_customer_id: int, part_num: str) -> int:
    sql = """
        INSERT INTO program_parts (customer_id, part_number)
        VALUES (:customer_id, :part_num)
        RETURNING id;
    """
    params = dict(
        customer_id=adp_customer_id,
        part_num=part_num
    )
    with session.begin():
        return ADP_DB.execute(session, sql, params).fetchone()[0]

@prog_parts.post('/{adp_customer_id}', tags=['jsonapi'])
async def add_program_parts(
        token: ADPPerm,
        adp_customer_id: int,
        session: NewSession,
        part: NewPartRObj,
    ):
    if token.permissions.get('adp') >= auth.ADPPermPriority.sca_employee:
        part_num = part.model_dump()['attributes']['part_number']
        try:
            new_id = await add_parts_to_program(session=session, adp_customer_id=adp_customer_id, part_num=part_num)
            return serializer.get_resource(
                session=session,
                api_type=ADP_PARTS_RESOURCE,
                query=PartsQuery(),
                obj_id=new_id,
                obj_only=True,
                permitted_ids=None
            )
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))