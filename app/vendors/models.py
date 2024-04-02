from pydantic import BaseModel, create_model, Field
from typing import Optional
from app.jsonapi.sqla_models import SCAVendor, SCAVendorInfo
from app.jsonapi.core_models import (
    JSONAPIRelationships,
    JSONAPIResourceObject,
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    Pagination,
    Query,
)

TYPE = SCAVendor.__jsonapi_type_override__
TYPE_INFO = SCAVendorInfo.__jsonapi_type_override__

## Vendor
class VendorAttributes(BaseModel):
    name: str
    headquarters: str
    description: str
    phone: int
    logo_path: str

class VendorFilters(BaseModel):
    filter_name: str = Field(default=None, alias='filter[name]')
    filter_headquarters: str = Field(default=None, alias='filter[headquarters]')
    filter_content: str = Field(default=None, alias='filter[content]')
    filter_category: str = Field(default=None, alias='filter[category]')
    filter_phone: str = Field(default=None, alias='filter[phone]')

class VendorRelationships(BaseModel):
    info: JSONAPIRelationships

class VendorFields(BaseModel):
    fields_vendors: str = Field(default=None, alias='fields[vendors]')
    fields_info: str = Field(default=None, alias='fields[info]')

class VendorResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = TYPE

class VendorResourceObject(VendorResourceIdentifier):
    attributes: VendorAttributes
    relationships: VendorRelationships

class VendorRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[VendorResourceIdentifier]|VendorResourceIdentifier

class VendorResponse(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[VendorResourceObject] | VendorResourceObject]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination] = None

class RelatedVendorResponse(VendorResponse):
    """When pulling as a related object, included is always empty
        and links are not in the object"""
    included: dict = {}
    links: dict = Field(default=None, exclude=True)

class NewVendorResouce(BaseModel):
    type: str = TYPE
    attributes: VendorAttributes
    relationships: Optional[VendorRelationships] = None

class NewVendor(BaseModel):
    data: NewVendorResouce

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
    data: Optional[list[VendorInfoResourceObject] | VendorInfoResourceObject]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination] = None

class NewVendorInfoResourceObject(BaseModel):
    type: str = TYPE_INFO
    attributes: VendorInfoAttributes
    relationships: VendorInfoRelationships

class ExistingVendorResourceObject(NewVendorInfoResourceObject):
    id: int

class NewVendorInfo(BaseModel):
    data: NewVendorInfoResourceObject

## Vendor Modifications
class VendorInfoModification(BaseModel):
    data: VendorInfoResourceObject

class VendorModification(BaseModel):
    data: VendorResourceObject

## base vendor query
_VendorQuery: type[BaseModel] = create_model(
    'VendorQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f"fields_{field}":(Optional[str], None) for field in VendorRelationships.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in VendorAttributes.model_fields.keys()},
)

class VendorQuery(_VendorQuery, BaseModel): ...

class VendorQueryJSONAPI(VendorFilters, VendorFields, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")