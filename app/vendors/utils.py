from sqlalchemy.orm import Session
from app.jsonapi.sqla_models import serializer, SCAVendorInfo, SCAVendor
from app.vendors.models import (
    VendorInfoModification,
    VendorModification,
    VendorResponse,
    VendorInfoResponse,
    NewVendor,
    NewVendorInfo,
)


def add_new_vendor_info(session: Session, payload: NewVendorInfo) -> VendorResponse:
    return serializer.post_collection(
        session=session,
        data=payload.model_dump(exclude_none=True),
        api_type=SCAVendorInfo.__jsonapi_type_override__,
    ).data


def modify_existing_vendor_info(
    session: Session, payload: VendorInfoModification, obj_id: int
) -> VendorInfoResponse:
    return serializer.patch_resource(
        session=session,
        json_data=payload.model_dump(exclude_none=True),
        api_type=SCAVendorInfo.__jsonapi_type_override__,
        obj_id=obj_id,
    ).data


def add_new_vendor(session: Session, payload: NewVendor) -> VendorResponse:
    return serializer.post_collection(
        session=session,
        data=payload.model_dump(exclude_none=True),
        api_type=SCAVendor.__jsonapi_type_override__,
    ).data


def modify_existing_vendor(
    session: Session, payload: VendorModification, obj_id: int
) -> VendorResponse:
    return serializer.patch_resource(
        session=session,
        json_data=payload.model_dump(exclude_none=True),
        api_type=SCAVendor.__jsonapi_type_override__,
        obj_id=obj_id,
    ).data


def delete_vendor_info(session: Session, obj_id: int):
    return serializer.delete_resource(
        session=session,
        data={},
        api_type=SCAVendorInfo.__jsonapi_type_override__,
        obj_id=obj_id,
    ).data


def delete_vendor(session: Session, obj_id: int):
    return serializer.delete_resource(
        session=session,
        data=None,
        api_type=SCAVendor.__jsonapi_type_override__,
        obj_id=obj_id,
    ).data
