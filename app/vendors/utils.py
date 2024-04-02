from sqlalchemy.orm import Session
from app.jsonapi.sqla_models import serializer, SCAVendorInfo, SCAVendor
from app.vendors.models import (
    VendorInfoModification, VendorModification,
    VendorResponse, VendorInfoResponse,
    NewVendor, NewVendorInfo
)

def add_new_vendor_info(session: Session, payload: NewVendorInfo) -> VendorResponse:
    return serializer.post_collection(
        session=session,
        data=payload.model_dump(),
        api_type=SCAVendorInfo.__jsonapi_type_override__
    )

def modify_existing_vendor_info(session: Session, payload: VendorInfoModification) -> VendorInfoResponse:
    return serializer.patch_resource(
        session=session,
        json_data=payload.model_dump(),
        api_type=SCAVendorInfo.__jsonapi_type_override__,
        obj_id=int(payload.data.id)
    )

def add_new_vendor(session: Session, payload: NewVendor) -> VendorResponse:
    return serializer.post_collection(
        session=session,
        data=payload.model_dump(),
        api_type=SCAVendor.__jsonapi_type_override__
    )

def modify_existing_vendor(session: Session, payload: VendorModification) -> VendorResponse:
    return serializer.patch_resource(
        session=session,
        json_data=payload.model_dump(),
        api_type=SCAVendor.__jsonapi_type_override__,
        obj_id=int(payload.data.id)
    )