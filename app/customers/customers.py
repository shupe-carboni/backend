from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from app import auth

from app.customers.models import CustomerQuery, CustomerResponse

customers = APIRouter(prefix='/customers', tags=['customers'])

@customers.get('')
async def customer_collection(
        query: CustomerQuery=Depends(), # type: ignore
        token: auth.VerifiedToken = Depends(auth.authenticate_auth0_token)
    ) -> CustomerResponse:
    raise HTTPException(status_code=501)