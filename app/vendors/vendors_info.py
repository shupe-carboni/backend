
from typing import Annotated
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app import auth
from app.db import SCA_DB
from app.jsonapi.sqla_models import SCAVendor
from app.vendors.models import (
    VendorResponse, VendorInfoResponse, VendorQuery,
    VendorQueryJSONAPI, RelatedVendorResponse,
    VendorRelationshipsResponse, NewVendor, NewVendorInfo,
    VendorModification
)
from app.vendors.utils import add_new_vendor_info, add_new_vendor, modify_existing_vendor, modify_existing_vendor_info

INFO_RESOURCE = SCAVendor.__jsonapi_type_override__
vendors_info = APIRouter(prefix='/info', tags=['vendor info'])

NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
VendorsPerm = Annotated[auth.VerifiedToken, Depends(auth.vendor_perms_present)]

def convert_query(query: VendorQuery) -> VendorQueryJSONAPI:
    return VendorQueryJSONAPI(**query.model_dump(exclude_none=True)).model_dump(by_alias=True, exclude_none=True)