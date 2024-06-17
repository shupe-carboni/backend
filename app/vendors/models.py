from pydantic import BaseModel, create_model, Field, ConfigDict
from typing import Optional
from app.jsonapi.sqla_models import SCAVendor, SCAVendorInfo, SCAVendorResourceMap
from app.jsonapi.core_models import (
    JSONAPIRelationships,
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIResponse,
    Query,
)

TYPE = SCAVendor.__jsonapi_type_override__
TYPE_INFO = SCAVendorInfo.__jsonapi_type_override__


## Vendor
class VendorAttributes(BaseModel):
    name: Optional[str] = None
    headquarters: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[int] = None
    logo_path: Optional[str] = None


class VendorFilters(BaseModel):
    filter_name: str = Field(default=None, alias="filter[name]")
    filter_headquarters: str = Field(default=None, alias="filter[headquarters]")
    filter_content: str = Field(default=None, alias="filter[content]")
    filter_category: str = Field(default=None, alias="filter[category]")
    filter_phone: str = Field(default=None, alias="filter[phone]")


class VendorRelationships(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    info: JSONAPIRelationships
    vendor_resource_mapping: JSONAPIRelationships = Field(
        alias="vendor-resource-mapping"
    )


class VendorFields(BaseModel):
    fields_vendors: str = Field(default=None, alias="fields[vendors]")
    fields_info: str = Field(default=None, alias="fields[info]")
    fields_vendor_resource_mapping: str = Field(
        default=None, alias="fields[vendor-resource-mapping]"
    )


class VendorResourceIdentifier(JSONAPIResourceIdentifier):
    type: str = TYPE


class VendorResourceObject(VendorResourceIdentifier):
    attributes: Optional[VendorAttributes] = None
    relationships: Optional[VendorRelationships] = None


class VendorRelationshipsResponse(JSONAPIRelationshipsResponse):
    data: list[VendorResourceIdentifier] | VendorResourceIdentifier


class VendorResponse(JSONAPIResponse):
    data: Optional[list[VendorResourceObject] | VendorResourceObject]


class RelatedVendorResponse(VendorResponse):
    """When pulling as a related object, included is always empty
    and links are not in the object"""

    included: dict = {}
    links: dict = Field(default=None, exclude=True)


class NewVendorResource(BaseModel):
    id: str
    type: str = TYPE
    attributes: Optional[VendorAttributes] = None
    relationships: Optional[VendorRelationships] = None


class NewVendor(BaseModel):
    data: NewVendorResource


## Vendor Info
class VendorInfoAttributes(BaseModel):
    category: Optional[str] = None
    content: Optional[str] = None


class VendorInfoFilters(BaseModel):
    filter_content: str = Field(default=None, alias="filter[content]")
    filter_category: str = Field(default=None, alias="filter[category]")


class VendorInfoRelationships(BaseModel):
    vendors: JSONAPIRelationships


class VendorInfoFields(BaseModel):
    fields_vendors: str = Field(default=None, alias="fields[vendors]")


class VendorInfoResourceObject(JSONAPIResourceIdentifier):
    attributes: Optional[VendorInfoAttributes] = None
    relationships: Optional[VendorInfoRelationships] = None


class VendorInfoResponse(JSONAPIResponse):
    data: Optional[list[VendorInfoResourceObject] | VendorInfoResourceObject]


class RelatedVendorInfoResponse(VendorInfoResponse):
    """When pulling as a related object, included is always empty
    and links are not in the object"""

    included: dict = {}
    links: dict = Field(default=None, exclude=True)


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
    "VendorQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorRelationships.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorAttributes.model_fields.keys()
    },
)
## vendor info query
_VendorInfoQuery: type[BaseModel] = create_model(
    "VendorInfoQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorInfoRelationships.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorInfoAttributes.model_fields.keys()
    },
)


class VendorQuery(_VendorQuery, BaseModel): ...


class VendorInfoQuery(_VendorInfoQuery, BaseModel): ...


class VendorQueryJSONAPI(VendorFilters, VendorFields, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class VendorInfoQueryJSONAPI(VendorInfoFilters, VendorInfoFields, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class VendorRelatedResourceRID(JSONAPIResourceIdentifier):
    type: str = SCAVendorResourceMap.__jsonapi_type_override__


class VendorResourceAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    resource_type: str = Field(default=None, alias="resource-type")
    resource: str
    category_name: str = Field(default=None, alias="category-name")


class VendorResourceRels(BaseModel):
    vendors: JSONAPIRelationships


class VendorResources(VendorRelatedResourceRID):
    attributes: VendorResourceAttrs
    relationships: VendorResourceRels


class VendorResourceResp(JSONAPIResponse):
    data: list[VendorResources] | VendorResources
