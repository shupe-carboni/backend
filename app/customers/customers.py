from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth

from app.customers.models import CustomerQuery, CustomerResponse

customers = APIRouter(prefix='/customers', tags=['customers'])

CustomersPerm = Annotated[auth.VerifiedToken, Depends(auth.customers_perms_present)]

@customers.get('')
async def customer_collection(
        token: CustomersPerm,
        query: CustomerQuery=Depends(), # type: ignore
    ) -> CustomerResponse:
    raise HTTPException(status_code=501)

@customers.get('/{customer_id}')
async def customer(
        token: CustomersPerm,
        customer_id: int,
        query: CustomerQuery=Depends(), # type: ignore
    ) -> CustomerResponse:
    raise HTTPException(status_code=501)