from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app import auth
from app.customers.models import CustomerQuery, CustomerResponse
from app.db.db import ADP_DB, SCA_DB
from app.db.sqla_models import SCACustomer, serializer

customers = APIRouter(prefix='/customers', tags=['customers'])

CustomersPerm = Annotated[auth.VerifiedToken, Depends(auth.customers_perms_present)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]

from pydantic import BaseModel
def convert_query(model: BaseModel):
    jsonapi_query = {}
    bracketed_params = {'fields','page'}
    for param, val in model.model_dump(exclude_none=True).items():
        param: str
        val: str
        if b_param := set(param.split('_')) & bracketed_params:
            b_param_val = b_param.pop()
            new_key = f"{b_param_val}[{param.removeprefix(b_param_val+'_').replace('_','-')}]"
            jsonapi_query.update({new_key: val})
        else:
            jsonapi_query.update({param: val})
    return jsonapi_query

@customers.get('')
async def customer_collection(
        session: NewSession,
        token: CustomersPerm,
        query: CustomerQuery=Depends(), # type: ignore
    ) -> CustomerResponse:
    jsonapi_query = convert_query(query)
    result = serializer.get_collection(session=session, query=jsonapi_query, model_obj=SCACustomer,user_id=0)
    import json
    print(json.dumps(result, indent=2))

    # try:
    #     return result
    # except Exception as e:
    #     raise HTTPException(status_code=501, detail=e)

@customers.get('/{customer_id}')
async def customer(
        token: CustomersPerm,
        customer_id: int,
        query: CustomerQuery=Depends(), # type: ignore
    ) -> CustomerResponse:
    raise HTTPException(status_code=501)