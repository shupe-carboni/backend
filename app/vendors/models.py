from pydantic import BaseModel, create_model, Field
from typing import Optional
from app.jsonapi.core_models import (
    JSONAPIRelationships,
    JSONAPIResourceObject,
    Pagination,
    JSONAPIResourceIdentifier,
    Query,
    JSONAPIRelationshipsResponse
)

## Vendor
class VendorAttributes(BaseModel):
    name: str
    headquarters: str
    description: str
    phone: int

class VendorRelationships(BaseModel):
    info: JSONAPIRelationships

class VendorResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = "sca_vendors"

class VendorResourceObject(VendorResourceIdentifier):
    attributes: VendorAttributes
    relationships: VendorRelationships

class VendorRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[VendorResourceIdentifier]|VendorResourceIdentifier

class VendorResponse(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[VendorResourceObject]]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination]

class RelatedVendorResponse(VendorResponse):
    """When pulling as a related object, included is always empty
        and links are not in the object"""
    included: dict = {}
    links: dict = Field(..., exclude=True)

## Vendor Info
class VendorInfoAttributes(BaseModel):
    category: str
    content: str

class VendorInfoRelationships(BaseModel):
    vendor: JSONAPIRelationships

class VendorInfoResourceObject(JSONAPIResourceIdentifier):
    attributes: VendorInfoAttributes 
    relationships: VendorInfoRelationships

class VendorInfoResponse(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[VendorInfoResourceObject]]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination]

class NewVendorInfoResourceObject(BaseModel):
    type: str = "sca-vendors"
    attributes: VendorInfoAttributes
    relationships: VendorInfoRelationships

## Vendor Modifications
class ExistingVendorInfo(NewVendorInfoResourceObject):
    id: str|int

VendorQuery: type[BaseModel] = create_model(
    'VendorQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f"fields_{field}":(Optional[str], None) for field in VendorRelationships.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in VendorAttributes.model_fields.keys()},
)
