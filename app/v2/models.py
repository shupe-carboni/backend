from pydantic import (
    BaseModel,
    Field,
    create_model,
    ConfigDict,
    WrapValidator,
)
from typing import Optional, Annotated
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResponse,
    Query,
    convert_query as __convert_query,
    set_none_default,
    NullableStr,
    NullableInt,
    NullableLongInt,
    NullableFloat,
    NullableDateTime,
    NullableBool,
    NullableStage,
    OptionalJSONAPIRelationships,
    OptionalDict,
    OptionalList,
    OptionalIntArr,
)

from app.jsonapi.sqla_models import Vendor


class VendorRID(JSONAPIResourceIdentifier):
    id: str
    type: str = Vendor.__jsonapi_type_override__


class VendorRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorRID]


class VendorAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: NullableStr
    headquarters: NullableStr
    description: NullableStr
    phone: NullableLongInt
    logo_path: NullableStr = Field(default=None, alias="logo-path")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors_attrs: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors-attrs"
    )
    vendor_products: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-products"
    )
    vendor_product_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-product-classes"
    )
    vendor_pricing_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-classes"
    )
    vendor_customers: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customers"
    )


OptionalVendorRels = Annotated[VendorRels, WrapValidator(set_none_default)]


class VendorFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_name: NullableStr = Field(default=None, alias="filter[name]")
    filter_headquarters: NullableStr = Field(default=None, alias="filter[headquarters]")
    filter_description: NullableStr = Field(default=None, alias="filter[description]")
    filter_phone: NullableStr = Field(default=None, alias="filter[phone]")
    filter_logo_path: NullableStr = Field(default=None, alias="filter[logo-path]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors_attrs: NullableStr = Field(
        default=None, alias="fields[vendors-attrs]"
    )
    fields_vendor_products: NullableStr = Field(
        default=None, alias="fields[vendor-products]"
    )
    fields_vendor_product_classes: NullableStr = Field(
        default=None, alias="fields[vendor-product-classes]"
    )
    fields_vendor_pricing_classes: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-classes]"
    )
    fields_vendor_customers: NullableStr = Field(
        default=None, alias="fields[vendor-customers]"
    )
    fields_vendors: NullableStr = Field(default=None, alias="fields[vendors]")


class VendorRObj(VendorRID):
    attributes: VendorAttrs
    relationships: VendorRels


class VendorCollectionResp(JSONAPIResponse):
    data: list[VendorRObj]


class VendorResourceResp(JSONAPIResponse):
    data: VendorRObj


class RelatedVendorResp(VendorResourceResp):
    included: OptionalList = Field(default_factory=list)
    links: OptionalDict = Field(exclude=True)


_VendorQuery: type[BaseModel] = create_model(
    "VendorQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorAttrs.model_fields.keys()
    },
    **{
        f"fields_vendors": (
            NullableStr,
            None,
        )
    },
)


class VendorQuery(_VendorQuery, BaseModel): ...


class VendorQueryJSONAPI(VendorFields, VendorFilters, Query):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: NullableStr = Field(default=None, alias="name")
    headquarters: NullableStr = Field(default=None, alias="headquarters")
    description: NullableStr = Field(default=None, alias="description")
    phone: NullableLongInt = Field(default=None, alias="phone")
    logo_path: NullableStr = Field(default=None, alias="logo-path")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorRObj(BaseModel):
    id: str
    type: str = Vendor.__jsonapi_type_override__
    attributes: ModVendorAttrs
    relationships: OptionalVendorRels


class ModVendor(BaseModel):
    data: ModVendorRObj


class NewVendorRObj(BaseModel):
    id: str
    type: str = Vendor.__jsonapi_type_override__
    attributes: ModVendorAttrs


class NewVendor(BaseModel):
    data: NewVendorRObj


from app.jsonapi.sqla_models import VendorsAttr


class VendorsAttrRID(JSONAPIResourceIdentifier):
    type: str = VendorsAttr.__jsonapi_type_override__


class VendorsAttrRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorsAttrRID]


class VendorsAttrAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    attr: NullableStr = Field(default=None, alias="attr")
    type: NullableStr = Field(default=None, alias="type")
    value: NullableStr = Field(default=None, alias="value")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorsAttrRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(default=None, alias="vendors")
    vendors_attrs_changelog: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors-attrs-changelog"
    )


class VendorsAttrFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_attr: NullableStr = Field(default=None, alias="filter[attr]")
    filter_type: NullableStr = Field(default=None, alias="filter[type]")
    filter_value: NullableStr = Field(default=None, alias="filter[value]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorsAttrFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors: NullableStr = Field(default=None, alias="fields[vendors]")
    fields_vendors_attrs_changelog: NullableStr = Field(
        default=None, alias="fields[vendors-attrs-changelog]"
    )
    fields_vendors_attrs: NullableStr = Field(
        default=None, alias="fields[vendors-attrs]"
    )


class VendorsAttrRObj(VendorsAttrRID):
    attributes: VendorsAttrAttrs
    relationships: VendorsAttrRels


class VendorsAttrCollectionResp(JSONAPIResponse):
    data: list[VendorsAttrRObj]


class VendorsAttrResourceResp(JSONAPIResponse):
    data: VendorsAttrRObj


class NewVendorsAttrRObj(BaseModel):
    type: str = VendorsAttr.__jsonapi_type_override__
    attributes: VendorsAttrAttrs
    relationships: VendorsAttrRels


class NewVendorsAttr(BaseModel):
    data: NewVendorsAttrRObj


class RelatedVendorsAttrResp(VendorsAttrCollectionResp):
    included: OptionalList
    links: OptionalDict


_VendorsAttrQuery: type[BaseModel] = create_model(
    "VendorsAttrQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorsAttrRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorsAttrAttrs.model_fields.keys()
    },
    **{
        f"fields_vendors_attrs": (
            NullableStr,
            None,
        )
    },
)


class VendorsAttrQuery(_VendorsAttrQuery, BaseModel): ...


class VendorsAttrQueryJSONAPI(VendorsAttrFields, VendorsAttrFilters, Query):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorsAttrAttrs(BaseModel):
    value: NullableStr = Field(default=None, alias="value")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorsAttrRObj(BaseModel):
    id: int
    type: str = VendorsAttr.__jsonapi_type_override__
    attributes: ModVendorsAttrAttrs
    relationships: VendorsAttrRels


class ModVendorsAttr(BaseModel):
    data: ModVendorsAttrRObj


from app.jsonapi.sqla_models import VendorProduct


class VendorProductRID(JSONAPIResourceIdentifier):
    type: str = VendorProduct.__jsonapi_type_override__


class VendorProductRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorProductRID]


class VendorProductCustomAttr(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    attr: NullableStr = Field(default=None, alias="attr")
    type: NullableStr = Field(default=None, alias="type")
    value: NullableStr = Field(default=None, alias="value")


OptionalVendorProductCustomAttr = Annotated[
    VendorProductCustomAttr, WrapValidator(set_none_default)
]
OptionalArrVendorProductCustomAttr = Annotated[
    list[VendorProductCustomAttr], WrapValidator(set_none_default)
]


class VendorProductAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_product_identifier: NullableStr = Field(
        default=None, alias="vendor-product-identifier"
    )
    vendor_product_description: NullableStr = Field(
        default=None, alias="vendor-product-description"
    )
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")
    attr_order: OptionalIntArr = Field(default=None, alias="attr-order")
    vendor_product_attrs: OptionalArrVendorProductCustomAttr = Field(
        default=None, exclude=True, alias="vendor-product-attrs"
    )


class VendorProductRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(default=None, alias="vendors")
    vendor_pricing_by_class: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-class"
    )
    vendor_pricing_by_customer: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-customer"
    )
    vendor_product_attrs: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-product-attrs"
    )
    vendor_product_to_class_mapping: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-product-to-class-mapping"
    )
    vendor_quote_products: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-quote-products"
    )


class VendorProductFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_vendor_product_identifier: NullableStr = Field(
        default=None, alias="filter[vendor-product-identifier]"
    )
    filter_vendor_product_description: NullableStr = Field(
        default=None, alias="filter[vendor-product-description]"
    )
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorProductFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors: NullableStr = Field(default=None, alias="fields[vendors]")
    fields_vendor_pricing_by_class: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-class]"
    )
    fields_vendor_pricing_by_customer: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )
    fields_vendor_product_attrs: NullableStr = Field(
        default=None, alias="fields[vendor-product-attrs]"
    )
    fields_vendor_product_to_class_mapping: NullableStr = Field(
        default=None, alias="fields[vendor-product-to-class-mapping]"
    )
    fields_vendor_quote_products: NullableStr = Field(
        default=None, alias="fields[vendor-quote-products]"
    )
    fields_vendor_products: NullableStr = Field(
        default=None, alias="fields[vendor-products]"
    )


class VendorProductRObj(VendorProductRID):
    attributes: VendorProductAttrs
    relationships: VendorProductRels


class VendorProductCollectionResp(JSONAPIResponse):
    data: list[VendorProductRObj]


class VendorProductResourceResp(JSONAPIResponse):
    data: VendorProductRObj


class NewVendorProductRObj(BaseModel):
    type: str = VendorProduct.__jsonapi_type_override__
    attributes: VendorProductAttrs
    relationships: VendorProductRels


class NewVendorProduct(BaseModel):
    data: NewVendorProductRObj


class RelatedVendorProductResp(VendorProductResourceResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorProductQuery: type[BaseModel] = create_model(
    "VendorProductQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorProductRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorProductAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_products": (
            NullableStr,
            None,
        )
    },
)


class VendorProductQuery(_VendorProductQuery, BaseModel): ...


class VendorProductQueryJSONAPI(VendorProductFields, VendorProductFilters, Query):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorProductAttrs(BaseModel):
    vendor_product_description: NullableStr = Field(
        default=None, alias="vendor-product-description"
    )
    attr_order: OptionalIntArr = Field(default=None, alias="attr-order")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorProductRObj(BaseModel):
    id: int
    type: str = VendorProduct.__jsonapi_type_override__
    attributes: ModVendorProductAttrs
    relationships: VendorProductRels


class ModVendorProduct(BaseModel):
    data: ModVendorProductRObj


from app.jsonapi.sqla_models import VendorProductAttr


class VendorProductAttrRID(JSONAPIResourceIdentifier):
    type: str = VendorProductAttr.__jsonapi_type_override__


class VendorProductAttrRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorProductAttrRID] | VendorProductAttrRID


class VendorProductAttrAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    attr: NullableStr = Field(default=None, alias="attr")
    type: NullableStr = Field(default=None, alias="type")
    value: NullableStr = Field(default=None, alias="value")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorProductAttrRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_products: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-products"
    )
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )


class VendorProductAttrFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_attr: NullableStr = Field(default=None, alias="filter[attr]")
    filter_type: NullableStr = Field(default=None, alias="filter[type]")
    filter_value: NullableStr = Field(default=None, alias="filter[value]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorProductAttrFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_products: NullableStr = Field(
        default=None, alias="fields[vendor-products]"
    )
    fields_vendor_product_attrs: NullableStr = Field(
        default=None, alias="fields[vendor-product-attrs]"
    )


class VendorProductAttrRObj(VendorProductAttrRID):
    attributes: VendorProductAttrAttrs
    relationships: VendorProductAttrRels


class VendorProductAttrCollectionResp(JSONAPIResponse):
    data: list[VendorProductAttrRObj]


class VendorProductAttrResourceResp(JSONAPIResponse):
    data: VendorProductAttrRObj


class NewVendorProductAttrRObj(BaseModel):
    type: str = VendorProductAttr.__jsonapi_type_override__
    attributes: VendorProductAttrAttrs
    relationships: VendorProductAttrRels


class NewVendorProductAttr(BaseModel):
    data: NewVendorProductAttrRObj


class RelatedVendorProductAttrResp(VendorProductAttrResourceResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorProductAttrQuery: type[BaseModel] = create_model(
    "VendorProductAttrQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorProductAttrRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorProductAttrAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_product_attrs": (
            NullableStr,
            None,
        )
    },
)


class VendorProductAttrQuery(_VendorProductAttrQuery, BaseModel): ...


class VendorProductAttrQueryJSONAPI(
    VendorProductAttrFields, VendorProductAttrFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorProductAttrAttrs(BaseModel):
    value: NullableStr = Field(default=None, alias="value")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorProductAttrRObj(BaseModel):
    id: int
    type: str = VendorProductAttr.__jsonapi_type_override__
    attributes: ModVendorProductAttrAttrs
    relationships: VendorProductAttrRels


class ModVendorProductAttr(BaseModel):
    data: ModVendorProductAttrRObj


from app.jsonapi.sqla_models import VendorProductClass


class VendorProductClassRID(JSONAPIResourceIdentifier):
    type: str = VendorProductClass.__jsonapi_type_override__


class VendorProductClassRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorProductClassRID]


class VendorProductClassAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: NullableStr = Field(default=None, alias="name")
    rank: NullableInt = Field(default=None, alias="rank")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorProductClassRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(default=None, alias="vendors")
    vendor_product_to_class_mapping: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-product-to-class-mapping"
    )
    vendor_product_class_discounts: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-product-class-discounts"
    )


class VendorProductClassFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_name: NullableStr = Field(default=None, alias="filter[name]")
    filter_rank: NullableStr = Field(default=None, alias="filter[rank]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorProductClassFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors: NullableStr = Field(default=None, alias="fields[vendors]")
    fields_vendor_product_to_class_mapping: NullableStr = Field(
        default=None, alias="fields[vendor-product-to-class-mapping]"
    )
    fields_vendor_product_class_discounts: NullableStr = Field(
        default=None, alias="fields[vendor-product-class-discounts]"
    )
    fields_vendor_product_classes: NullableStr = Field(
        default=None, alias="fields[vendor-product-classes]"
    )


class VendorProductClassRObj(VendorProductClassRID):
    attributes: VendorProductClassAttrs
    relationships: VendorProductClassRels


class VendorProductClassCollectionResp(JSONAPIResponse):
    data: list[VendorProductClassRObj]


class VendorProductClassResourceResp(JSONAPIResponse):
    data: VendorProductClassRObj


class NewVendorProductClassRObj(BaseModel):
    type: str = VendorProductClass.__jsonapi_type_override__
    attributes: VendorProductClassAttrs
    relationships: VendorProductClassRels


class NewVendorProductClass(BaseModel):
    data: NewVendorProductClassRObj


class RelatedVendorProductClassResp(VendorProductClassResourceResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorProductClassQuery: type[BaseModel] = create_model(
    "VendorProductClassQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorProductClassRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorProductClassAttrs.model_fields.keys()
    },
    **{f"fields_vendor_product_classes": (NullableStr, None)},
)


class VendorProductClassQuery(_VendorProductClassQuery, BaseModel): ...


class VendorProductClassQueryJSONAPI(
    VendorProductClassFields, VendorProductClassFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorProductClassAttrs(BaseModel):
    name: NullableStr = Field(default=None, alias="name")
    rank: NullableInt = Field(default=None, alias="rank")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorProductClassRObj(BaseModel):
    id: int
    type: str = VendorProductClass.__jsonapi_type_override__
    attributes: ModVendorProductClassAttrs
    relationships: VendorProductClassRels


class ModVendorProductClass(BaseModel):
    data: ModVendorProductClassRObj


from app.jsonapi.sqla_models import VendorProductToClassMapping


class VendorProductToClassMappingRID(JSONAPIResourceIdentifier):
    type: str = VendorProductToClassMapping.__jsonapi_type_override__


class VendorProductToClassMappingRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorProductToClassMappingRID] | VendorProductToClassMappingRID


class VendorProductToClassMappingAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


OptionalVendorProductToClassMappingAttrs = Annotated[
    VendorProductToClassMappingAttrs, WrapValidator(set_none_default)
]


class VendorProductToClassMappingRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_product_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-product-classes"
    )
    vendor_products: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-products"
    )


class VendorProductToClassMappingFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorProductToClassMappingFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_product_classes: NullableStr = Field(
        default=None, alias="fields[vendor-product-classes]"
    )
    fields_vendor_products: NullableStr = Field(
        default=None, alias="fields[vendor-products]"
    )
    fields_vendor_product_to_class_mapping: NullableStr = Field(
        default=None, alias="fields[vendor-product-to-class-mapping]"
    )


class VendorProductToClassMappingRObj(VendorProductToClassMappingRID):
    attributes: VendorProductToClassMappingAttrs
    relationships: VendorProductToClassMappingRels


class VendorProductToClassMappingResp(JSONAPIResponse):
    data: list[VendorProductToClassMappingRObj] | VendorProductToClassMappingRObj


class NewVendorProductToClassMappingRObj(BaseModel):
    type: str = VendorProductToClassMapping.__jsonapi_type_override__
    attributes: OptionalVendorProductToClassMappingAttrs
    relationships: VendorProductToClassMappingRels


class NewVendorProductToClassMapping(BaseModel):
    data: NewVendorProductToClassMappingRObj


class RelatedVendorProductToClassMappingResp(VendorProductToClassMappingResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorProductToClassMappingQuery: type[BaseModel] = create_model(
    "VendorProductToClassMappingQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorProductToClassMappingRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorProductToClassMappingAttrs.model_fields.keys()
    },
    **{f"fields_vendor_product_to_class_mapping": (NullableStr, None)},
)


class VendorProductToClassMappingQuery(
    _VendorProductToClassMappingQuery, BaseModel
): ...


class VendorProductToClassMappingQueryJSONAPI(
    VendorProductToClassMappingFields, VendorProductToClassMappingFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorProductToClassMappingAttrs(BaseModel):
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorProductToClassMappingRObj(BaseModel):
    id: int
    type: str = VendorProductToClassMapping.__jsonapi_type_override__
    attributes: ModVendorProductToClassMappingAttrs
    relationships: VendorProductToClassMappingRels


class ModVendorProductToClassMapping(BaseModel):
    data: ModVendorProductToClassMappingRObj


from app.jsonapi.sqla_models import VendorPricingClass


class VendorPricingClassRID(JSONAPIResourceIdentifier):
    type: str = VendorPricingClass.__jsonapi_type_override__


class VendorPricingClassRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorPricingClassRID]


class VendorPricingClassAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: NullableStr = Field(default=None, alias="name")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorPricingClassRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(default=None, alias="vendors")
    vendor_pricing_by_class: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-class"
    )
    vendor_pricing_by_customer: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-customer"
    )
    vendor_customer_pricing_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customer-pricing-classes"
    )
    vendor_customer_pricing_classes_changelog: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customer-pricing-classes-changelog"
    )


class VendorPricingClassFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_name: NullableStr = Field(default=None, alias="filter[name]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorPricingClassFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors: NullableStr = Field(default=None, alias="fields[vendors]")
    fields_vendor_pricing_by_class: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-class]"
    )
    fields_vendor_pricing_by_customer: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )
    fields_vendor_customer_pricing_classes: NullableStr = Field(
        default=None, alias="fields[vendor-customer-pricing-classes]"
    )
    fields_vendor_customer_pricing_classes_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-customer-pricing-classes-changelog]"
    )
    fields_vendor_pricing_classes: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-classes]"
    )


class VendorPricingClassRObj(VendorPricingClassRID):
    attributes: VendorPricingClassAttrs
    relationships: VendorPricingClassRels


class VendorPricingClassCollectionResp(JSONAPIResponse):
    data: list[VendorPricingClassRObj]


class VendorPricingClassResourceResp(JSONAPIResponse):
    data: VendorPricingClassRObj


class NewVendorPricingClassRObj(BaseModel):
    type: str = VendorPricingClass.__jsonapi_type_override__
    attributes: VendorPricingClassAttrs
    relationships: VendorPricingClassRels


class NewVendorPricingClass(BaseModel):
    data: NewVendorPricingClassRObj


class RelatedVendorPricingClassResp(VendorPricingClassResourceResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorPricingClassQuery: type[BaseModel] = create_model(
    "VendorPricingClassQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorPricingClassRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorPricingClassAttrs.model_fields.keys()
    },
    **{f"fields_vendor_pricing_classes": (NullableStr, None)},
)


class VendorPricingClassQuery(_VendorPricingClassQuery, BaseModel): ...


class VendorPricingClassQueryJSONAPI(
    VendorPricingClassFields, VendorPricingClassFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorPricingClassAttrs(BaseModel):
    name: NullableStr = Field(default=None, alias="name")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorPricingClassRObj(BaseModel):
    id: int
    type: str = VendorPricingClass.__jsonapi_type_override__
    attributes: ModVendorPricingClassAttrs
    relationships: VendorPricingClassRels


class ModVendorPricingClass(BaseModel):
    data: ModVendorPricingClassRObj


from app.jsonapi.sqla_models import VendorPricingByClass


class VendorPricingByClassRID(JSONAPIResourceIdentifier):
    type: str = VendorPricingByClass.__jsonapi_type_override__


class VendorPricingByClassRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorPricingByClassRID] | VendorPricingByClassRID


class VendorPricingByClassAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    price: NullableInt = Field(default=None, alias="price")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorPricingByClassRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_pricing_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-classes"
    )
    vendor_products: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-products"
    )
    vendor_pricing_by_class_changelog: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-class-changelog"
    )
    customer_pricing_by_class: OptionalJSONAPIRelationships = Field(
        default=None, alias="customer-pricing-by-class"
    )


class VendorPricingByClassFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_price: NullableStr = Field(default=None, alias="filter[price]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorPricingByClassFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_classes: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-classes]"
    )
    fields_vendor_products: NullableStr = Field(
        default=None, alias="fields[vendor-products]"
    )
    fields_vendor_pricing_by_class_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-class-changelog]"
    )
    fields_customer_pricing_by_class: NullableStr = Field(
        default=None, alias="fields[customer-pricing-by-class]"
    )
    fields_vendor_pricing_by_class: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-class]"
    )


class VendorPricingByClassRObj(VendorPricingByClassRID):
    attributes: VendorPricingByClassAttrs
    relationships: VendorPricingByClassRels


class VendorPricingByClassResp(JSONAPIResponse):
    data: list[VendorPricingByClassRObj] | VendorPricingByClassRObj


class NewVendorPricingByClassRObj(BaseModel):
    type: str = VendorPricingByClass.__jsonapi_type_override__
    attributes: VendorPricingByClassAttrs
    relationships: VendorPricingByClassRels


class NewVendorPricingByClass(BaseModel):
    data: NewVendorPricingByClassRObj


class RelatedVendorPricingByClassResp(VendorPricingByClassResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorPricingByClassQuery: type[BaseModel] = create_model(
    "VendorPricingByClassQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorPricingByClassRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorPricingByClassAttrs.model_fields.keys()
    },
    **{f"fields_vendor_pricing_by_class": (NullableStr, None)},
)


class VendorPricingByClassQuery(_VendorPricingByClassQuery, BaseModel): ...


class VendorPricingByClassQueryJSONAPI(
    VendorPricingByClassFields, VendorPricingByClassFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorPricingByClassAttrs(BaseModel):
    price: NullableInt = Field(default=None, alias="price")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorPricingByClassRObj(BaseModel):
    id: int
    type: str = VendorPricingByClass.__jsonapi_type_override__
    attributes: ModVendorPricingByClassAttrs
    relationships: VendorPricingByClassRels


class ModVendorPricingByClass(BaseModel):
    data: ModVendorPricingByClassRObj


from app.jsonapi.sqla_models import VendorPricingByClassChangelog


class VendorPricingByClassChangelogRID(JSONAPIResourceIdentifier):
    type: str = VendorPricingByClassChangelog.__jsonapi_type_override__


class VendorPricingByClassChangelogRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorPricingByClassChangelogRID]


class VendorPricingByClassChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    price: NullableInt = Field(default=None, alias="price")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")
    timestamp: NullableDateTime = Field(default=None, alias="timestamp")


class VendorPricingByClassChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_pricing_by_class: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-class"
    )


class VendorPricingByClassChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_price: NullableStr = Field(default=None, alias="filter[price]")
    filter_timestamp: NullableStr = Field(default=None, alias="filter[timestamp]")


class VendorPricingByClassChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_by_class: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-class]"
    )
    fields_vendor_pricing_by_class_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-class-changelog]"
    )


class VendorPricingByClassChangelogRObj(VendorPricingByClassChangelogRID):
    attributes: VendorPricingByClassChangelogAttrs
    relationships: VendorPricingByClassChangelogRels


class VendorPricingByClassChangelogResp(JSONAPIResponse):
    data: list[VendorPricingByClassChangelogRObj] | VendorPricingByClassChangelogRObj


class RelatedVendorPricingByClassChangelogResp(VendorPricingByClassChangelogResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorPricingByClassChangelogQuery: type[BaseModel] = create_model(
    "VendorPricingByClassChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorPricingByClassChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorPricingByClassChangelogAttrs.model_fields.keys()
    },
    **{f"fields_vendor_pricing_by_class_changelog": (NullableStr, None)},
)


class VendorPricingByClassChangelogQuery(
    _VendorPricingByClassChangelogQuery, BaseModel
): ...


class VendorPricingByClassChangelogQueryJSONAPI(
    VendorPricingByClassChangelogFields, VendorPricingByClassChangelogFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorPricingByCustomer


class VendorPricingByCustomerRID(JSONAPIResourceIdentifier):
    type: str = VendorPricingByCustomer.__jsonapi_type_override__


class VendorPricingByCustomerRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorPricingByCustomerRID] | VendorPricingByCustomerRID


class VendorPricingByCustomerAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    use_as_override: NullableBool = Field(default=None, alias="use-as-override")
    price: NullableInt = Field(default=None, alias="price")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorPricingByCustomerRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_customers: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customers"
    )
    vendor_products: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-products"
    )
    vendor_pricing_by_customer_attrs: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-customer-attrs"
    )
    vendor_pricing_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-classes"
    )
    vendor_pricing_by_customer_changelog: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-customer-changelog"
    )
    customer_pricing_by_customer: OptionalJSONAPIRelationships = Field(
        default=None, alias="customer-pricing-by-customer"
    )
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )


class VendorPricingByCustomerFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_use_as_override: NullableStr = Field(
        default=None, alias="filter[use-as-override]"
    )
    filter_price: NullableStr = Field(default=None, alias="filter[price]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorPricingByCustomerFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customers: NullableStr = Field(
        default=None, alias="fields[vendor-customers]"
    )
    fields_vendor_products: NullableStr = Field(
        default=None, alias="fields[vendor-products]"
    )
    fields_vendor_pricing_by_customer_attrs: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-customer-attrs]"
    )
    fields_vendor_pricing_classes: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-classes]"
    )
    fields_vendor_pricing_by_customer_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-customer-changelog]"
    )
    fields_customer_pricing_by_customer: NullableStr = Field(
        default=None, alias="fields[customer-pricing-by-customer]"
    )
    fields_vendor_pricing_by_customer: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )


class VendorPricingByCustomerRObj(VendorPricingByCustomerRID):
    attributes: VendorPricingByCustomerAttrs
    relationships: VendorPricingByCustomerRels


class VendorPricingByCustomerCollectionResp(JSONAPIResponse):
    data: list[VendorPricingByCustomerRObj]


class VendorPricingByCustomerResourceResp(JSONAPIResponse):
    data: VendorPricingByCustomerRObj


class NewVendorPricingByCustomerRObj(BaseModel):
    type: str = VendorPricingByCustomer.__jsonapi_type_override__
    attributes: VendorPricingByCustomerAttrs
    relationships: VendorPricingByCustomerRels


class NewVendorPricingByCustomer(BaseModel):
    data: NewVendorPricingByCustomerRObj


class RelatedVendorPricingByCustomerResp(VendorPricingByCustomerResourceResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorPricingByCustomerQuery: type[BaseModel] = create_model(
    "VendorPricingByCustomerQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorPricingByCustomerRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorPricingByCustomerAttrs.model_fields.keys()
    },
    **{f"fields_vendor_pricing_by_customer": (NullableStr, None)},
)


class VendorPricingByCustomerQuery(_VendorPricingByCustomerQuery, BaseModel): ...


class VendorPricingByCustomerQueryJSONAPI(
    VendorPricingByCustomerFields, VendorPricingByCustomerFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorPricingByCustomerAttrs(BaseModel):
    use_as_override: NullableBool = Field(default=None, alias="use-as-override")
    price: NullableInt = Field(default=None, alias="price")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorPricingByCustomerRObj(BaseModel):
    id: int
    type: str = VendorPricingByCustomer.__jsonapi_type_override__
    attributes: VendorPricingByCustomerAttrs
    relationships: VendorPricingByCustomerRels


class ModVendorPricingByCustomer(BaseModel):
    data: ModVendorPricingByCustomerRObj


from app.jsonapi.sqla_models import VendorCustomer


class VendorCustomerRID(JSONAPIResourceIdentifier):
    type: str = VendorCustomer.__jsonapi_type_override__


class VendorCustomerRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorCustomerRID]


class VendorCustomerCustomAttr(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    attr: NullableStr = Field(default=None, alias="attr")
    type: NullableStr = Field(default=None, alias="type")
    value: NullableStr = Field(default=None, alias="value")


OptionalVendorCustomerCustomAttr = Annotated[
    VendorCustomerCustomAttr, WrapValidator(set_none_default)
]
OptionalArrVendorCustomerCustomAttr = Annotated[
    list[VendorCustomerCustomAttr], WrapValidator(set_none_default)
]


class VendorCustomerAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: NullableStr = Field(default=None, alias="name")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")
    vendor_customer_attrs: OptionalArrVendorCustomerCustomAttr = Field(
        default=None, exclude=True, alias="vendor-customer-attrs"
    )


class VendorCustomerRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(default=None, alias="vendors")
    vendor_pricing_by_customer: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-customer"
    )
    vendor_customer_pricing_classes_changelog: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customer-pricing-classes-changelog"
    )
    vendor_customer_pricing_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customer-pricing-classes"
    )
    vendor_customer_changelog: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customer-changelog"
    )
    vendor_quotes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-quotes"
    )
    vendor_customer_attrs: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customer-attrs"
    )
    vendor_product_class_discounts: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-product-class-discounts"
    )
    customer_location_mapping: OptionalJSONAPIRelationships = Field(
        default=None, alias="customer-location-mapping"
    )


class VendorCustomerFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_name: NullableStr = Field(default=None, alias="filter[name]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")
    filter_vendor_product_classes__name: NullableStr = Field(
        default=None, alias="filter[vendor-product-classes.name]"
    )
    filter_vendor_product_classes__rank: NullableStr = Field(
        default=None, alias="filter[vendor-product-classes.rank]"
    )


class VendorCustomerFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors: NullableStr = Field(default=None, alias="fields[vendors]")
    fields_vendor_pricing_by_customer: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )
    fields_vendor_customer_pricing_classes_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-customer-pricing-classes-changelog]"
    )
    fields_vendor_customer_pricing_classes: NullableStr = Field(
        default=None, alias="fields[vendor-customer-pricing-classes]"
    )
    fields_vendor_customer_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-customer-changelog]"
    )
    fields_vendor_quotes: NullableStr = Field(
        default=None, alias="fields[vendor-quotes]"
    )
    fields_vendor_customer_attrs: NullableStr = Field(
        default=None, alias="fields[vendor-customer-attrs]"
    )
    fields_vendor_product_class_discounts: NullableStr = Field(
        default=None, alias="fields[vendor-product-class-discounts]"
    )
    fields_customer_location_mapping: NullableStr = Field(
        default=None, alias="fields[customer-location-mapping]"
    )
    fields_vendor_customers: NullableStr = Field(
        default=None, alias="fields[vendor-customers]"
    )


class VendorCustomerRObj(VendorCustomerRID):
    attributes: VendorCustomerAttrs
    relationships: VendorCustomerRels


class VendorCustomerCollectionResp(JSONAPIResponse):
    data: list[VendorCustomerRObj]


class VendorCustomerResourceResp(JSONAPIResponse):
    data: VendorCustomerRObj


class NewVendorCustomerRObj(BaseModel):
    type: str = VendorCustomer.__jsonapi_type_override__
    attributes: VendorCustomerAttrs
    relationships: VendorCustomerRels


class NewVendorCustomer(BaseModel):
    data: NewVendorCustomerRObj


class RelatedVendorCustomerResp(VendorCustomerResourceResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


vendor_customer_field_and_filter_params = (
    *VendorCustomerFields.model_fields.keys(),
    *VendorCustomerFilters.model_fields.keys(),
)
standard_query_params = {
    field: (field_info.annotation, field_info)
    for field, field_info in Query.model_fields.items()
}
vendor_customer_query_params = {
    field: (NullableStr, None) for field in vendor_customer_field_and_filter_params
}

_VendorCustomerQuery: type[BaseModel] = create_model(
    "VendorCustomerQuery", **standard_query_params, **vendor_customer_query_params
)


class VendorCustomerQuery(_VendorCustomerQuery, BaseModel): ...


class VendorCustomerQueryJSONAPI(VendorCustomerFields, VendorCustomerFilters, Query):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorCustomerAttrs(BaseModel):
    name: NullableStr = Field(default=None, alias="name")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorCustomerRObj(BaseModel):
    id: int
    type: str = VendorCustomer.__jsonapi_type_override__
    attributes: ModVendorCustomerAttrs
    relationships: VendorCustomerRels


class ModVendorCustomer(BaseModel):
    data: ModVendorCustomerRObj


from app.jsonapi.sqla_models import VendorPricingByCustomerChangelog


class VendorPricingByCustomerChangelogRID(JSONAPIResourceIdentifier):
    type: str = VendorPricingByCustomerChangelog.__jsonapi_type_override__


class VendorPricingByCustomerChangelogRelResp(JSONAPIRelationshipsResponse):
    data: (
        list[VendorPricingByCustomerChangelogRID] | VendorPricingByCustomerChangelogRID
    )


class VendorPricingByCustomerChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    price: NullableInt = Field(default=None, alias="price")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")
    timestamp: NullableDateTime = Field(default=None, alias="timestamp")


class VendorPricingByCustomerChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_pricing_by_customer: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-customer"
    )


class VendorPricingByCustomerChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_price: NullableStr = Field(default=None, alias="filter[price]")
    filter_timestamp: NullableStr = Field(default=None, alias="filter[timestamp]")


class VendorPricingByCustomerChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_by_customer: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )
    fields_vendor_pricing_by_customer_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-customer-changelog]"
    )


class VendorPricingByCustomerChangelogRObj(VendorPricingByCustomerChangelogRID):
    attributes: VendorPricingByCustomerChangelogAttrs
    relationships: VendorPricingByCustomerChangelogRels


class VendorPricingByCustomerChangelogResp(JSONAPIResponse):
    data: (
        list[VendorPricingByCustomerChangelogRObj]
        | VendorPricingByCustomerChangelogRObj
    )


class RelatedVendorPricingByCustomerChangelogResp(VendorPricingByCustomerChangelogResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorPricingByCustomerChangelogQuery: type[BaseModel] = create_model(
    "VendorPricingByCustomerChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorPricingByCustomerChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorPricingByCustomerChangelogAttrs.model_fields.keys()
    },
    **{f"fields_vendor_pricing_by_customer_changelog": (NullableStr, None)},
)


class VendorPricingByCustomerChangelogQuery(
    _VendorPricingByCustomerChangelogQuery, BaseModel
): ...


class VendorPricingByCustomerChangelogQueryJSONAPI(
    VendorPricingByCustomerChangelogFields,
    VendorPricingByCustomerChangelogFilters,
    Query,
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorProductClassDiscount


class VendorProductClassDiscountRID(JSONAPIResourceIdentifier):
    type: str = VendorProductClassDiscount.__jsonapi_type_override__


class VendorProductClassDiscountRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorProductClassDiscountRID] | VendorProductClassDiscountRID


class VendorProductClassDiscountAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    discount: NullableFloat = Field(default=None, alias="discount")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorProductClassDiscountRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )
    base_price_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="base-price-classes"
    )
    label_price_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="label-price-classes"
    )
    vendor_customers: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customers"
    )
    vendor_product_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-product-classes"
    )
    vendor_product_class_discounts_changelog: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-product-class-discounts-changelog"
    )


class VendorProductClassDiscountFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_discount: NullableStr = Field(default=None, alias="filter[discount]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorProductClassDiscountFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customers: NullableStr = Field(
        default=None, alias="fields[vendor-customers]"
    )
    fields_vendor_product_classes: NullableStr = Field(
        default=None, alias="fields[vendor-product-classes]"
    )
    fields_vendor_product_class_discounts_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-product-class-discounts-changelog]"
    )
    fields_vendor_product_class_discounts: NullableStr = Field(
        default=None, alias="fields[vendor-product-class-discounts]"
    )


class VendorProductClassDiscountRObj(VendorProductClassDiscountRID):
    attributes: VendorProductClassDiscountAttrs
    relationships: VendorProductClassDiscountRels


class VendorProductClassDiscountCollectionResp(JSONAPIResponse):
    data: list[VendorProductClassDiscountRObj]


class VendorProductClassDiscountResourceResp(JSONAPIResponse):
    data: VendorProductClassDiscountRObj


class NewVendorProductClassDiscountRObj(BaseModel):
    type: str = VendorProductClassDiscount.__jsonapi_type_override__
    attributes: VendorProductClassDiscountAttrs
    relationships: VendorProductClassDiscountRels


class NewVendorProductClassDiscount(BaseModel):
    data: NewVendorProductClassDiscountRObj


class RelatedVendorProductClassDiscountResp(VendorProductClassDiscountResourceResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorProductClassDiscountQuery: type[BaseModel] = create_model(
    "VendorProductClassDiscountQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorProductClassDiscountRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorProductClassDiscountAttrs.model_fields.keys()
    },
    **{f"fields_vendor_product_class_discounts": (NullableStr, None)},
)


class VendorProductClassDiscountQuery(_VendorProductClassDiscountQuery, BaseModel): ...


class VendorProductClassDiscountQueryJSONAPI(
    VendorProductClassDiscountFields, VendorProductClassDiscountFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorProductClassDiscountAttrs(BaseModel):
    discount: NullableFloat = Field(default=None, alias="discount")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorProductClassDiscountRObj(BaseModel):
    id: int
    type: str = VendorProductClassDiscount.__jsonapi_type_override__
    attributes: VendorProductClassDiscountAttrs
    relationships: VendorProductClassDiscountRels


class ModVendorProductClassDiscount(BaseModel):
    data: ModVendorProductClassDiscountRObj


from app.jsonapi.sqla_models import VendorPricingByCustomerAttr


class VendorPricingByCustomerAttrRID(JSONAPIResourceIdentifier):
    type: str = VendorPricingByCustomerAttr.__jsonapi_type_override__


class VendorPricingByCustomerAttrRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorPricingByCustomerAttrRID] | VendorPricingByCustomerAttrRID


class VendorPricingByCustomerAttrAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    attr: NullableStr = Field(default=None, alias="attr")
    type: NullableStr = Field(default=None, alias="type")
    value: NullableStr = Field(default=None, alias="value")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorPricingByCustomerAttrRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_pricing_by_customer: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-customer"
    )


class VendorPricingByCustomerAttrFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_attr: NullableStr = Field(default=None, alias="filter[attr]")
    filter_type: NullableStr = Field(default=None, alias="filter[type]")
    filter_value: NullableStr = Field(default=None, alias="filter[value]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorPricingByCustomerAttrFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_by_customer: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )
    fields_vendor_pricing_by_customer_attrs: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-customer-attrs]"
    )


class VendorPricingByCustomerAttrRObj(VendorPricingByCustomerAttrRID):
    attributes: VendorPricingByCustomerAttrAttrs
    relationships: VendorPricingByCustomerAttrRels


class VendorPricingByCustomerAttrResp(JSONAPIResponse):
    data: list[VendorPricingByCustomerAttrRObj] | VendorPricingByCustomerAttrRObj


class NewVendorPricingByCustomerAttrRObj(BaseModel):
    type: str = VendorPricingByCustomerAttr.__jsonapi_type_override__
    attributes: VendorPricingByCustomerAttrAttrs
    relationships: VendorPricingByCustomerAttrRels


class NewVendorPricingByCustomerAttr(BaseModel):
    data: NewVendorPricingByCustomerAttrRObj


class ModVendorPricingByCustomerAttrAttrs(BaseModel):
    value: NullableStr = Field(default=None, alias="value")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorPricingByCustomerAttrRObj(BaseModel):
    id: int
    type: str = VendorPricingByCustomerAttr.__jsonapi_type_override__
    attributes: ModVendorPricingByCustomerAttrAttrs
    relationships: VendorPricingByCustomerAttrRels


class ModVendorPricingByCustomerAttr(BaseModel):
    data: ModVendorPricingByCustomerAttrRObj


class RelatedVendorPricingByCustomerAttrResp(VendorPricingByCustomerAttrResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorPricingByCustomerAttrQuery: type[BaseModel] = create_model(
    "VendorPricingByCustomerAttrQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorPricingByCustomerAttrRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorPricingByCustomerAttrAttrs.model_fields.keys()
    },
    **{f"fields_vendor_pricing_by_customer_attrs": (NullableStr, None)},
)


class VendorPricingByCustomerAttrQuery(
    _VendorPricingByCustomerAttrQuery, BaseModel
): ...


class VendorPricingByCustomerAttrQueryJSONAPI(
    VendorPricingByCustomerAttrFields, VendorPricingByCustomerAttrFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorProductClassDiscountsChangelog


class VendorProductClassDiscountsChangelogRID(JSONAPIResourceIdentifier):
    type: str = VendorProductClassDiscountsChangelog.__jsonapi_type_override__


class VendorProductClassDiscountsChangelogRelResp(JSONAPIRelationshipsResponse):
    data: (
        list[VendorProductClassDiscountsChangelogRID]
        | VendorProductClassDiscountsChangelogRID
    )


class VendorProductClassDiscountsChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    discount: NullableFloat = Field(default=None, alias="discount")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")
    timestamp: NullableDateTime = Field(default=None, alias="timestamp")


class VendorProductClassDiscountsChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_product_class_discounts: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-product-class-discounts"
    )


class VendorProductClassDiscountsChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_discount: NullableStr = Field(default=None, alias="filter[discount]")
    filter_timestamp: NullableStr = Field(default=None, alias="filter[timestamp]")


class VendorProductClassDiscountsChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_product_class_discounts: NullableStr = Field(
        default=None, alias="fields[vendor-product-class-discounts]"
    )
    fields_vendor_product_class_discounts_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-product-class-discounts-changelog]"
    )


class VendorProductClassDiscountsChangelogRObj(VendorProductClassDiscountsChangelogRID):
    attributes: VendorProductClassDiscountsChangelogAttrs
    relationships: VendorProductClassDiscountsChangelogRels


class VendorProductClassDiscountsChangelogResp(JSONAPIResponse):
    data: (
        list[VendorProductClassDiscountsChangelogRObj]
        | VendorProductClassDiscountsChangelogRObj
    )


class RelatedVendorProductClassDiscountsChangelogResp(
    VendorProductClassDiscountsChangelogResp
):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorProductClassDiscountsChangelogQuery: type[BaseModel] = create_model(
    "VendorProductClassDiscountsChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorProductClassDiscountsChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorProductClassDiscountsChangelogAttrs.model_fields.keys()
    },
    **{f"fields_vendor_product_class_discounts_changelog": (NullableStr, None)},
)


class VendorProductClassDiscountsChangelogQuery(
    _VendorProductClassDiscountsChangelogQuery, BaseModel
): ...


class VendorProductClassDiscountsChangelogQueryJSONAPI(
    VendorProductClassDiscountsChangelogFields,
    VendorProductClassDiscountsChangelogFilters,
    Query,
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorQuote


class VendorQuoteRID(JSONAPIResourceIdentifier):
    type: str = VendorQuote.__jsonapi_type_override__


class VendorQuoteRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorQuoteRID] | VendorQuoteRID


class VendorQuoteAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_quote_number: NullableStr = Field(default=None, alias="vendor-quote-number")
    job_name: NullableStr = Field(default=None, alias="job-name")
    status: NullableStage = Field(default=None, alias="status")
    quote_doc: NullableStr = Field(default=None, alias="quote-doc")
    plans_doc: NullableStr = Field(default=None, alias="plans-doc")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorQuoteRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_customers: JSONAPIRelationships = Field(
        default=None, alias="vendor-customers"
    )
    vendor_quote_products: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-quote-products"
    )
    places: OptionalJSONAPIRelationships = Field(default=None, alias="places")
    vendor_quotes_changelog: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-quotes-changelog"
    )
    vendor_quotes_attrs: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-quotes-attrs"
    )
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )


class VendorQuoteFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_vendor_quote_number: NullableStr = Field(
        default=None, alias="filter[vendor-quote-number]"
    )
    filter_job_name: NullableStr = Field(default=None, alias="filter[job-name]")
    filter_status: NullableStr = Field(default=None, alias="filter[status]")
    filter_quote_doc: NullableStr = Field(default=None, alias="filter[quote-doc]")
    filter_plans_doc: NullableStr = Field(default=None, alias="filter[plans-doc]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorQuoteFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customers: NullableStr = Field(
        default=None, alias="fields[vendor-customers]"
    )
    fields_vendor_quote_products: NullableStr = Field(
        default=None, alias="fields[vendor-quote-products]"
    )
    fields_places: NullableStr = Field(default=None, alias="fields[places]")
    fields_vendor_quotes_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-quotes-changelog]"
    )
    fields_vendor_quotes_attrs: NullableStr = Field(
        default=None, alias="fields[vendor-quotes-attrs]"
    )
    fields_vendor_quotes: NullableStr = Field(
        default=None, alias="fields[vendor-quotes]"
    )


class VendorQuoteRObj(VendorQuoteRID):
    attributes: VendorQuoteAttrs
    relationships: VendorQuoteRels


class VendorQuoteCollectionResp(JSONAPIResponse):
    data: list[VendorQuoteRObj]


class VendorQuoteResourceResp(JSONAPIResponse):
    data: VendorQuoteRObj


class NewVendorQuoteRObj(BaseModel):
    type: str = VendorQuote.__jsonapi_type_override__
    attributes: VendorQuoteAttrs
    relationships: VendorQuoteRels


class NewVendorQuote(BaseModel):
    data: NewVendorQuoteRObj


class RelatedVendorQuoteResp(VendorQuoteResourceResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorQuoteQuery: type[BaseModel] = create_model(
    "VendorQuoteQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorQuoteRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorQuoteAttrs.model_fields.keys()
    },
    **{f"fields_vendor_quotes": (NullableStr, None)},
)


class VendorQuoteQuery(_VendorQuoteQuery, BaseModel): ...


class VendorQuoteQueryJSONAPI(VendorQuoteFields, VendorQuoteFilters, Query):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorQuoteAttrs(BaseModel):
    vendor_quote_number: NullableStr = Field(default=None, alias="vendor-quote-number")
    status: NullableStage = Field(default=None, alias="status")
    quote_doc: NullableStr = Field(default=None, alias="quote-doc")
    plans_doc: NullableStr = Field(default=None, alias="plans-doc")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorQuoteRObj(BaseModel):
    id: int
    type: str = VendorQuote.__jsonapi_type_override__
    attributes: ModVendorQuoteAttrs
    relationships: VendorQuoteRels


class ModVendorQuote(BaseModel):
    data: ModVendorQuoteRObj


from app.jsonapi.sqla_models import CustomerLocationMapping


class CustomerLocationMappingRID(JSONAPIResourceIdentifier):
    type: str = CustomerLocationMapping.__jsonapi_type_override__


class CustomerLocationMappingRelResp(JSONAPIRelationshipsResponse):
    data: list[CustomerLocationMappingRID] | CustomerLocationMappingRID


class CustomerLocationMappingAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


OptionalCustomerLocationMappingAttrs = Annotated[
    CustomerLocationMappingAttrs, WrapValidator(set_none_default)
]


class CustomerLocationMappingRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_customers: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customers"
    )
    customer_locations: OptionalJSONAPIRelationships = Field(
        default=None, alias="customer-locations"
    )


class CustomerLocationMappingFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class CustomerLocationMappingFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customers: NullableStr = Field(
        default=None, alias="fields[vendor-customers]"
    )
    fields_customer_locations: NullableStr = Field(
        default=None, alias="fields[customer-locations]"
    )
    fields_customer_location_mapping: NullableStr = Field(
        default=None, alias="fields[customer-location-mapping]"
    )


class CustomerLocationMappingRObj(CustomerLocationMappingRID):
    attributes: CustomerLocationMappingAttrs
    relationships: CustomerLocationMappingRels


class CustomerLocationMappingResp(JSONAPIResponse):
    data: list[CustomerLocationMappingRObj] | CustomerLocationMappingRObj


class NewCustomerLocationMappingRObj(BaseModel):
    type: str = CustomerLocationMapping.__jsonapi_type_override__
    attributes: OptionalCustomerLocationMappingAttrs
    relationships: CustomerLocationMappingRels


class NewCustomerLocationMapping(BaseModel):
    data: NewCustomerLocationMappingRObj


class RelatedCustomerLocationMappingResp(CustomerLocationMappingResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_CustomerLocationMappingQuery: type[BaseModel] = create_model(
    "CustomerLocationMappingQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in CustomerLocationMappingRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in CustomerLocationMappingAttrs.model_fields.keys()
    },
    **{f"fields_customer_location_mapping": (NullableStr, None)},
)


class CustomerLocationMappingQuery(_CustomerLocationMappingQuery, BaseModel): ...


class CustomerLocationMappingQueryJSONAPI(
    CustomerLocationMappingFields, CustomerLocationMappingFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorQuoteProduct


class VendorQuoteProductRID(JSONAPIResourceIdentifier):
    type: str = VendorQuoteProduct.__jsonapi_type_override__


class VendorQuoteProductRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorQuoteProductRID] | VendorQuoteProductRID


class VendorQuoteProductAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    tag: NullableStr = Field(default=None, alias="tag")
    competitor_model: NullableStr = Field(default=None, alias="competitor-model")
    qty: NullableInt = Field(default=None, alias="qty")
    price: NullableInt = Field(default=None, alias="price")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorQuoteProductRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_quotes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-quotes"
    )
    vendor_products: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-products"
    )
    vendor_quote_products_changelog: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-quote-products-changelog"
    )
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )


class VendorQuoteProductFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_tag: NullableStr = Field(default=None, alias="filter[tag]")
    filter_competitor_model: NullableStr = Field(
        default=None, alias="filter[competitor-model]"
    )
    filter_qty: NullableStr = Field(default=None, alias="filter[qty]")
    filter_price: NullableStr = Field(default=None, alias="filter[price]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorQuoteProductFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_quotes: NullableStr = Field(
        default=None, alias="fields[vendor-quotes]"
    )
    fields_vendor_products: NullableStr = Field(
        default=None, alias="fields[vendor-products]"
    )
    fields_vendor_quote_products_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-quote-products-changelog]"
    )
    fields_vendor_quote_products: NullableStr = Field(
        default=None, alias="fields[vendor-quote-products]"
    )


class VendorQuoteProductRObj(VendorQuoteProductRID):
    attributes: VendorQuoteProductAttrs
    relationships: VendorQuoteProductRels


class VendorQuoteProductResp(JSONAPIResponse):
    data: list[VendorQuoteProductRObj] | VendorQuoteProductRObj


class NewVendorQuoteProductRObj(BaseModel):
    type: str = VendorQuoteProduct.__jsonapi_type_override__
    attributes: VendorQuoteProductAttrs
    relationships: VendorQuoteProductRels


class NewVendorQuoteProduct(BaseModel):
    data: NewVendorQuoteProductRObj


class RelatedVendorQuoteProductResp(VendorQuoteProductResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorQuoteProductQuery: type[BaseModel] = create_model(
    "VendorQuoteProductQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorQuoteProductRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorQuoteProductAttrs.model_fields.keys()
    },
    **{f"fields_vendor_quote_products": (NullableStr, None)},
)


class VendorQuoteProductQuery(_VendorQuoteProductQuery, BaseModel): ...


class VendorQuoteProductQueryJSONAPI(
    VendorQuoteProductFields, VendorQuoteProductFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorQuoteProductAttrs(BaseModel):
    qty: NullableInt = Field(default=None, alias="qty")
    price: NullableInt = Field(default=None, alias="price")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorQuoteProductRObj(BaseModel):
    id: int
    type: str = VendorQuoteProduct.__jsonapi_type_override__
    attributes: ModVendorQuoteProductAttrs
    relationships: VendorQuoteProductRels


class ModVendorQuoteProduct(BaseModel):
    data: ModVendorQuoteProductRObj


from app.jsonapi.sqla_models import VendorQuoteChangelog


class VendorQuoteChangelogRID(JSONAPIResourceIdentifier):
    type: str = VendorQuoteChangelog.__jsonapi_type_override__


class VendorQuoteChangelogRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorQuoteChangelogRID] | VendorQuoteChangelogRID


class VendorQuoteChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    status: NullableStage = Field(default=None, alias="status")
    timestamp: NullableDateTime = Field(default=None, alias="timestamp")


class VendorQuoteChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_quotes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-quotes"
    )


class VendorQuoteChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_status: NullableStr = Field(default=None, alias="filter[status]")
    filter_timestamp: NullableStr = Field(default=None, alias="filter[timestamp]")


class VendorQuoteChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_quotes: NullableStr = Field(
        default=None, alias="fields[vendor-quotes]"
    )
    fields_vendor_quotes_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-quotes-changelog]"
    )


class VendorQuoteChangelogRObj(VendorQuoteChangelogRID):
    attributes: VendorQuoteChangelogAttrs
    relationships: VendorQuoteChangelogRels


class VendorQuoteChangelogResp(JSONAPIResponse):
    data: list[VendorQuoteChangelogRObj] | VendorQuoteChangelogRObj


class RelatedVendorQuoteChangelogResp(VendorQuoteChangelogResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorQuoteChangelogQuery: type[BaseModel] = create_model(
    "VendorQuoteChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorQuoteChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorQuoteChangelogAttrs.model_fields.keys()
    },
    **{f"fields_vendor_quotes_changelog": (NullableStr, None)},
)


class VendorQuoteChangelogQuery(_VendorQuoteChangelogQuery, BaseModel): ...


class VendorQuoteChangelogQueryJSONAPI(
    VendorQuoteChangelogFields, VendorQuoteChangelogFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorQuoteProductChangelog


class VendorQuoteProductChangelogRID(JSONAPIResourceIdentifier):
    type: str = VendorQuoteProductChangelog.__jsonapi_type_override__


class VendorQuoteProductChangelogRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorQuoteProductChangelogRID] | VendorQuoteProductChangelogRID


class VendorQuoteProductChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    qty: NullableInt = Field(default=None, alias="qty")
    price: NullableInt = Field(default=None, alias="price")
    timestamp: NullableDateTime = Field(default=None, alias="timestamp")


class VendorQuoteProductChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_quote_products: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-quote-products"
    )


class VendorQuoteProductChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_qty: NullableStr = Field(default=None, alias="filter[qty]")
    filter_price: NullableStr = Field(default=None, alias="filter[price]")
    filter_timestamp: NullableStr = Field(default=None, alias="filter[timestamp]")


class VendorQuoteProductChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_quote_products: NullableStr = Field(
        default=None, alias="fields[vendor-quote-products]"
    )
    fields_vendor_quote_products_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-quote-products-changelog]"
    )


class VendorQuoteProductChangelogRObj(VendorQuoteProductChangelogRID):
    attributes: VendorQuoteProductChangelogAttrs
    relationships: VendorQuoteProductChangelogRels


class VendorQuoteProductChangelogResp(JSONAPIResponse):
    data: list[VendorQuoteProductChangelogRObj] | VendorQuoteProductChangelogRObj


class RelatedVendorQuoteProductChangelogResp(VendorQuoteProductChangelogResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorQuoteProductChangelogQuery: type[BaseModel] = create_model(
    "VendorQuoteProductChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorQuoteProductChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorQuoteProductChangelogAttrs.model_fields.keys()
    },
    **{f"fields_vendor_quote_products_changelog": (NullableStr, None)},
)


class VendorQuoteProductChangelogQuery(
    _VendorQuoteProductChangelogQuery, BaseModel
): ...


class VendorQuoteProductChangelogQueryJSONAPI(
    VendorQuoteProductChangelogFields, VendorQuoteProductChangelogFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorCustomerPricingClass


class VendorCustomerPricingClassRID(JSONAPIResourceIdentifier):
    type: str = VendorCustomerPricingClass.__jsonapi_type_override__


class VendorCustomerPricingClassRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorCustomerPricingClassRID] | VendorCustomerPricingClassRID


class VendorCustomerPricingClassAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


OptionalVendorCustomerPricingClassAttrs = Annotated[
    VendorCustomerPricingClassAttrs, WrapValidator(set_none_default)
]


class VendorCustomerPricingClassRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_pricing_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-classes"
    )
    vendor_customers: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customers"
    )


class VendorCustomerPricingClassFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorCustomerPricingClassFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_classes: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-classes]"
    )
    fields_vendor_customers: NullableStr = Field(
        default=None, alias="fields[vendor-customers]"
    )
    fields_vendor_customer_pricing_classes: NullableStr = Field(
        default=None, alias="fields[vendor-customer-pricing-classes]"
    )


class VendorCustomerPricingClassRObj(VendorCustomerPricingClassRID):
    attributes: VendorCustomerPricingClassAttrs
    relationships: VendorCustomerPricingClassRels


class VendorCustomerPricingClassCollectionResp(JSONAPIResponse):
    data: list[VendorCustomerPricingClassRObj]


class VendorCustomerPricingClassResourceResp(JSONAPIResponse):
    data: VendorCustomerPricingClassRObj


class NewVendorCustomerPricingClassRObj(BaseModel):
    type: str = VendorCustomerPricingClass.__jsonapi_type_override__
    attributes: OptionalVendorCustomerPricingClassAttrs
    relationships: VendorCustomerPricingClassRels


class ModVendorCustomerPricingClassRObj(BaseModel):
    id: int
    type: str = VendorCustomerPricingClass.__jsonapi_type_override__
    attributes: OptionalVendorCustomerPricingClassAttrs
    relationships: VendorCustomerPricingClassRels


class NewVendorCustomerPricingClass(BaseModel):
    data: NewVendorCustomerPricingClassRObj


class ModVendorCustomerPricingClass(BaseModel):
    data: ModVendorCustomerPricingClassRObj


class RelatedVendorCustomerPricingClassResp(VendorCustomerPricingClassResourceResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorCustomerPricingClassQuery: type[BaseModel] = create_model(
    "VendorCustomerPricingClassQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorCustomerPricingClassRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorCustomerPricingClassAttrs.model_fields.keys()
    },
    **{f"fields_vendor_customer_pricing_classes": (NullableStr, None)},
)


class VendorCustomerPricingClassQuery(_VendorCustomerPricingClassQuery, BaseModel): ...


class VendorCustomerPricingClassQueryJSONAPI(
    VendorCustomerPricingClassFields, VendorCustomerPricingClassFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorCustomerPricingClassesChangelog


class VendorCustomerPricingClassesChangelogRID(JSONAPIResourceIdentifier):
    type: str = VendorCustomerPricingClassesChangelog.__jsonapi_type_override__


class VendorCustomerPricingClassesChangelogRelResp(JSONAPIRelationshipsResponse):
    data: (
        list[VendorCustomerPricingClassesChangelogRID]
        | VendorCustomerPricingClassesChangelogRID
    )


class VendorCustomerPricingClassesChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    timestamp: NullableDateTime = Field(default=None, alias="timestamp")


class VendorCustomerPricingClassesChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_pricing_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-classes"
    )
    vendor_customers: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customers"
    )


class VendorCustomerPricingClassesChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_timestamp: NullableStr = Field(default=None, alias="filter[timestamp]")


class VendorCustomerPricingClassesChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_classes: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-classes]"
    )
    fields_vendor_customers: NullableStr = Field(
        default=None, alias="fields[vendor-customers]"
    )
    fields_vendor_customer_pricing_classes_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-customer-pricing-classes-changelog]"
    )


class VendorCustomerPricingClassesChangelogRObj(
    VendorCustomerPricingClassesChangelogRID
):
    attributes: VendorCustomerPricingClassesChangelogAttrs
    relationships: VendorCustomerPricingClassesChangelogRels


class VendorCustomerPricingClassesChangelogResp(JSONAPIResponse):
    data: (
        list[VendorCustomerPricingClassesChangelogRObj]
        | VendorCustomerPricingClassesChangelogRObj
    )


class RelatedVendorCustomerPricingClassesChangelogResp(
    VendorCustomerPricingClassesChangelogResp
):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorCustomerPricingClassesChangelogQuery: type[BaseModel] = create_model(
    "VendorCustomerPricingClassesChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorCustomerPricingClassesChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorCustomerPricingClassesChangelogAttrs.model_fields.keys()
    },
    **{f"fields_vendor_customer_pricing_classes_changelog": (NullableStr, None)},
)


class VendorCustomerPricingClassesChangelogQuery(
    _VendorCustomerPricingClassesChangelogQuery, BaseModel
): ...


class VendorCustomerPricingClassesChangelogQueryJSONAPI(
    VendorCustomerPricingClassesChangelogFields,
    VendorCustomerPricingClassesChangelogFilters,
    Query,
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorCustomerChangelog


class VendorCustomerChangelogRID(JSONAPIResourceIdentifier):
    type: str = VendorCustomerChangelog.__jsonapi_type_override__


class VendorCustomerChangelogRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorCustomerChangelogRID] | VendorCustomerChangelogRID


class VendorCustomerChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: NullableStr = Field(default=None, alias="name")
    timestamp: NullableDateTime = Field(default=None, alias="timestamp")


class VendorCustomerChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_customers: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customers"
    )


class VendorCustomerChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_name: NullableStr = Field(default=None, alias="filter[name]")
    filter_timestamp: NullableStr = Field(default=None, alias="filter[timestamp]")


class VendorCustomerChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customers: NullableStr = Field(
        default=None, alias="fields[vendor-customers]"
    )
    fields_vendor_customer_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-customer-changelog]"
    )


class VendorCustomerChangelogRObj(VendorCustomerChangelogRID):
    attributes: VendorCustomerChangelogAttrs
    relationships: VendorCustomerChangelogRels


class VendorCustomerChangelogResp(JSONAPIResponse):
    data: list[VendorCustomerChangelogRObj] | VendorCustomerChangelogRObj


class RelatedVendorCustomerChangelogResp(VendorCustomerChangelogResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorCustomerChangelogQuery: type[BaseModel] = create_model(
    "VendorCustomerChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorCustomerChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorCustomerChangelogAttrs.model_fields.keys()
    },
    **{f"fields_vendor_customer_changelog": (NullableStr, None)},
)


class VendorCustomerChangelogQuery(_VendorCustomerChangelogQuery, BaseModel): ...


class VendorCustomerChangelogQueryJSONAPI(
    VendorCustomerChangelogFields, VendorCustomerChangelogFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorCustomerAttr


class VendorCustomerAttrRID(JSONAPIResourceIdentifier):
    type: str = VendorCustomerAttr.__jsonapi_type_override__


class VendorCustomerAttrRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorCustomerAttrRID] | VendorCustomerAttrRID


class VendorCustomerAttrAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    attr: NullableStr = Field(default=None, alias="attr")
    type: NullableStr = Field(default=None, alias="type")
    value: NullableStr = Field(default=None, alias="value")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorCustomerAttrRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_customers: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customers"
    )
    vendor_customer_attrs_changelog: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customer-attrs-changelog"
    )


class VendorCustomerAttrFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_attr: NullableStr = Field(default=None, alias="filter[attr]")
    filter_type: NullableStr = Field(default=None, alias="filter[type]")
    filter_value: NullableStr = Field(default=None, alias="filter[value]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorCustomerAttrFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customers: NullableStr = Field(
        default=None, alias="fields[vendor-customers]"
    )
    fields_vendor_customer_attrs_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-customer-attrs-changelog]"
    )
    fields_vendor_customer_attrs: NullableStr = Field(
        default=None, alias="fields[vendor-customer-attrs]"
    )


class VendorCustomerAttrRObj(VendorCustomerAttrRID):
    attributes: VendorCustomerAttrAttrs
    relationships: VendorCustomerAttrRels


class VendorCustomerAttrResp(JSONAPIResponse):
    data: list[VendorCustomerAttrRObj] | VendorCustomerAttrRObj


class NewVendorCustomerAttrRObj(BaseModel):
    type: str = VendorCustomerAttr.__jsonapi_type_override__
    attributes: VendorCustomerAttrAttrs
    relationships: VendorCustomerAttrRels


class NewVendorCustomerAttr(BaseModel):
    data: NewVendorCustomerAttrRObj


class RelatedVendorCustomerAttrResp(VendorCustomerAttrResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorCustomerAttrQuery: type[BaseModel] = create_model(
    "VendorCustomerAttrQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorCustomerAttrRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorCustomerAttrAttrs.model_fields.keys()
    },
    **{f"fields_vendor_customer_attrs": (NullableStr, None)},
)


class VendorCustomerAttrQuery(_VendorCustomerAttrQuery, BaseModel): ...


class VendorCustomerAttrQueryJSONAPI(
    VendorCustomerAttrFields, VendorCustomerAttrFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorCustomerAttrAttrs(BaseModel):
    value: NullableStr = Field(default=None, alias="value")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorCustomerAttrRObj(BaseModel):
    id: int
    type: str = VendorCustomerAttr.__jsonapi_type_override__
    attributes: ModVendorCustomerAttrAttrs
    relationships: VendorCustomerAttrRels


class ModVendorCustomerAttr(BaseModel):
    data: ModVendorCustomerAttrRObj


from app.jsonapi.sqla_models import VendorQuoteAttr


class VendorQuoteAttrRID(JSONAPIResourceIdentifier):
    type: str = VendorQuoteAttr.__jsonapi_type_override__


class VendorQuoteAttrRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorQuoteAttrRID] | VendorQuoteAttrRID


class VendorQuoteAttrAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    attr: NullableStr = Field(default=None, alias="attr")
    type: NullableStr = Field(default=None, alias="type")
    value: NullableStr = Field(default=None, alias="value")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorQuoteAttrRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_quotes: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-quotes"
    )
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )


class VendorQuoteAttrFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_attr: NullableStr = Field(default=None, alias="filter[attr]")
    filter_type: NullableStr = Field(default=None, alias="filter[type]")
    filter_value: NullableStr = Field(default=None, alias="filter[value]")
    filter_deleted_at: NullableStr = Field(default=None, alias="filter[deleted-at]")


class VendorQuoteAttrFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_quotes: NullableStr = Field(
        default=None, alias="fields[vendor-quotes]"
    )
    fields_vendor_quotes_attrs: NullableStr = Field(
        default=None, alias="fields[vendor-quotes-attrs]"
    )


class VendorQuoteAttrRObj(VendorQuoteAttrRID):
    attributes: VendorQuoteAttrAttrs
    relationships: VendorQuoteAttrRels


class VendorQuoteAttrResp(JSONAPIResponse):
    data: list[VendorQuoteAttrRObj] | VendorQuoteAttrRObj


class NewVendorQuoteAttrRObj(BaseModel):
    type: str = VendorQuoteAttr.__jsonapi_type_override__
    attributes: VendorQuoteAttrAttrs
    relationships: VendorQuoteAttrRels


class NewVendorQuoteAttr(BaseModel):
    data: NewVendorQuoteAttrRObj


class RelatedVendorQuoteAttrResp(VendorQuoteAttrResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorQuoteAttrQuery: type[BaseModel] = create_model(
    "VendorQuoteAttrQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorQuoteAttrRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorQuoteAttrAttrs.model_fields.keys()
    },
    **{f"fields_vendor_quotes_attrs": (NullableStr, None)},
)


class VendorQuoteAttrQuery(_VendorQuoteAttrQuery, BaseModel): ...


class VendorQuoteAttrQueryJSONAPI(VendorQuoteAttrFields, VendorQuoteAttrFilters, Query):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorQuoteAttrAttrs(BaseModel):
    value: NullableStr = Field(default=None, alias="value")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class ModVendorQuoteAttrRObj(BaseModel):
    id: int
    type: str = VendorQuoteAttr.__jsonapi_type_override__
    attributes: ModVendorQuoteAttrAttrs
    relationships: VendorQuoteAttrRels


class ModVendorQuoteAttr(BaseModel):
    data: ModVendorQuoteAttrRObj


from app.jsonapi.sqla_models import CustomerPricingByClass


class CustomerPricingByClassRID(JSONAPIResourceIdentifier):
    type: str = CustomerPricingByClass.__jsonapi_type_override__


class CustomerPricingByClassRelResp(JSONAPIRelationshipsResponse):
    data: list[CustomerPricingByClassRID] | CustomerPricingByClassRID


class CustomerPricingByClassAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    # gets hard deleted


OptionalCustomerPricingByClassAttrs = Annotated[
    CustomerPricingByClassAttrs, WrapValidator(set_none_default)
]


class CustomerPricingByClassRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_pricing_by_class: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-class"
    )
    users: OptionalJSONAPIRelationships = Field(default=None, alias="users")


class CustomerPricingByClassFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class CustomerPricingByClassFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_by_class: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-class]"
    )
    fields_users: NullableStr = Field(default=None, alias="fields[users]")
    fields_customer_pricing_by_class: NullableStr = Field(
        default=None, alias="fields[customer-pricing-by-class]"
    )


class CustomerPricingByClassRObj(CustomerPricingByClassRID):
    attributes: CustomerPricingByClassAttrs
    relationships: CustomerPricingByClassRels


class CustomerPricingByClassResp(JSONAPIResponse):
    data: list[CustomerPricingByClassRObj] | CustomerPricingByClassRObj


class NewCustomerPricingByClassRObj(BaseModel):
    type: str = CustomerPricingByClass.__jsonapi_type_override__
    attributes: OptionalCustomerPricingByClassAttrs
    relationships: CustomerPricingByClassRels


class NewCustomerPricingByClass(BaseModel):
    data: NewCustomerPricingByClassRObj


class RelatedCustomerPricingByClassResp(CustomerPricingByClassResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_CustomerPricingByClassQuery: type[BaseModel] = create_model(
    "CustomerPricingByClassQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in CustomerPricingByClassRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in CustomerPricingByClassAttrs.model_fields.keys()
    },
    **{f"fields_customer_pricing_by_class": (NullableStr, None)},
)


class CustomerPricingByClassQuery(_CustomerPricingByClassQuery, BaseModel): ...


class CustomerPricingByClassQueryJSONAPI(
    CustomerPricingByClassFields, CustomerPricingByClassFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import CustomerPricingByCustomer


class CustomerPricingByCustomerRID(JSONAPIResourceIdentifier):
    type: str = CustomerPricingByCustomer.__jsonapi_type_override__


class CustomerPricingByCustomerRelResp(JSONAPIRelationshipsResponse):
    data: list[CustomerPricingByCustomerRID] | CustomerPricingByCustomerRID


class CustomerPricingByCustomerAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    # gets hard deleted


OptionalCustomerPricingByCustomerAttrs = Annotated[
    CustomerPricingByCustomerAttrs, WrapValidator(set_none_default)
]


class CustomerPricingByCustomerRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_pricing_by_customer: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-customer"
    )
    users: OptionalJSONAPIRelationships = Field(default=None, alias="users")


class CustomerPricingByCustomerFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class CustomerPricingByCustomerFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_by_customer: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )
    fields_users: NullableStr = Field(default=None, alias="fields[users]")
    fields_customer_pricing_by_customer: NullableStr = Field(
        default=None, alias="fields[customer-pricing-by-customer]"
    )


class CustomerPricingByCustomerRObj(CustomerPricingByCustomerRID):
    attributes: OptionalCustomerPricingByCustomerAttrs
    relationships: CustomerPricingByCustomerRels


class CustomerPricingByCustomerResp(JSONAPIResponse):
    data: list[CustomerPricingByCustomerRObj] | CustomerPricingByCustomerRObj


class RelatedCustomerPricingByCustomerResp(CustomerPricingByCustomerResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


class NewCustomerPricingByCustomerRObj(BaseModel):
    type: str = CustomerPricingByCustomer.__jsonapi_type_override__
    attributes: OptionalCustomerPricingByCustomerAttrs
    relationships: CustomerPricingByCustomerRels


class NewCustomerPricingByCustomer(BaseModel):
    data: NewCustomerPricingByCustomerRObj


_CustomerPricingByCustomerQuery: type[BaseModel] = create_model(
    "CustomerPricingByCustomerQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in CustomerPricingByCustomerRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in CustomerPricingByCustomerAttrs.model_fields.keys()
    },
    **{f"fields_customer_pricing_by_customer": (NullableStr, None)},
)


class CustomerPricingByCustomerQuery(_CustomerPricingByCustomerQuery, BaseModel): ...


class CustomerPricingByCustomerQueryJSONAPI(
    CustomerPricingByCustomerFields, CustomerPricingByCustomerFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorCustomerAttrChangelog


class VendorCustomerAttrChangelogRID(JSONAPIResourceIdentifier):
    type: str = VendorCustomerAttrChangelog.__jsonapi_type_override__


class VendorCustomerAttrChangelogRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorCustomerAttrChangelogRID] | VendorCustomerAttrChangelogRID


class VendorCustomerAttrChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: NullableStr
    type: NullableStr
    value: NullableStr = Field(default=None, alias="value")
    timestamp: NullableDateTime = Field(default=None, alias="timestamp")


class VendorCustomerAttrChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_customer_attrs: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customer-attrs"
    )


class VendorCustomerAttrChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_value: NullableStr = Field(default=None, alias="filter[value]")
    filter_timestamp: NullableStr = Field(default=None, alias="filter[timestamp]")


class VendorCustomerAttrChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customer_attrs: NullableStr = Field(
        default=None, alias="fields[vendor-customer-attrs]"
    )
    fields_vendor_customer_attrs_changelog: NullableStr = Field(
        default=None, alias="fields[vendor-customer-attrs-changelog]"
    )


class VendorCustomerAttrChangelogRObj(VendorCustomerAttrChangelogRID):
    attributes: VendorCustomerAttrChangelogAttrs
    relationships: VendorCustomerAttrChangelogRels


class VendorCustomerAttrChangelogResp(JSONAPIResponse):
    data: list[VendorCustomerAttrChangelogRObj] | VendorCustomerAttrChangelogRObj


class RelatedVendorCustomerAttrChangelogResp(VendorCustomerAttrChangelogResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorCustomerAttrChangelogQuery: type[BaseModel] = create_model(
    "VendorCustomerAttrChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorCustomerAttrChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorCustomerAttrChangelogAttrs.model_fields.keys()
    },
    **{f"fields_vendor_customer_attrs_changelog": (NullableStr, None)},
)


class VendorCustomerAttrChangelogQuery(
    _VendorCustomerAttrChangelogQuery, BaseModel
): ...


class VendorCustomerAttrChangelogQueryJSONAPI(
    VendorCustomerAttrChangelogFields, VendorCustomerAttrChangelogFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorsAttrsChangelog


class VendorsAttrsChangelogRID(JSONAPIResourceIdentifier):
    type: str = VendorsAttrsChangelog.__jsonapi_type_override__


class VendorsAttrsChangelogRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorsAttrsChangelogRID] | VendorsAttrsChangelogRID


class VendorsAttrsChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    value: NullableStr = Field(default=None, alias="value")
    timestamp: NullableDateTime = Field(default=None, alias="timestamp")


class VendorsAttrsChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors_attrs: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors-attrs"
    )


class VendorsAttrsChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_type: NullableStr = Field(default=None, alias="filter[type]")
    filter_value: NullableStr = Field(default=None, alias="filter[value]")
    filter_timestamp: NullableStr = Field(default=None, alias="filter[timestamp]")


class VendorsAttrsChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors_attrs: NullableStr = Field(
        default=None, alias="fields[vendors-attrs]"
    )
    fields_vendors_attrs_changelog: NullableStr = Field(
        default=None, alias="fields[vendors-attrs-changelog]"
    )


class VendorsAttrsChangelogRObj(VendorsAttrsChangelogRID):
    attributes: VendorsAttrsChangelogAttrs
    relationships: VendorsAttrsChangelogRels


class VendorsAttrsChangelogCollectionResp(JSONAPIResponse):
    data: list[VendorsAttrsChangelogRObj]


class VendorsAttrsChangelogResourceResp(JSONAPIResponse):
    data: VendorsAttrsChangelogRObj


class RelatedVendorsAttrsChangelogResp(VendorsAttrsChangelogResourceResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorsAttrsChangelogQuery: type[BaseModel] = create_model(
    "VendorsAttrsChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorsAttrsChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorsAttrsChangelogAttrs.model_fields.keys()
    },
    **{f"fields_vendors_attrs_changelog": (NullableStr, None)},
)


class VendorsAttrsChangelogQuery(_VendorsAttrsChangelogQuery, BaseModel): ...


class VendorsAttrsChangelogQueryJSONAPI(
    VendorsAttrsChangelogFields, VendorsAttrsChangelogFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorProductClassDiscountFuture


class VendorProductClassDiscountFutureRID(JSONAPIResourceIdentifier):
    type: str = VendorProductClassDiscountFuture.__jsonapi_type_override__


class VendorProductClassDiscountFutureRelResp(JSONAPIRelationshipsResponse):
    data: (
        list[VendorProductClassDiscountFutureRID] | VendorProductClassDiscountFutureRID
    )


class VendorProductClassDiscountFutureAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    discount: NullableFloat = Field(default=None, alias="discount")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")


class VendorProductClassDiscountFutureRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_product_class_discounts: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-product-class-discounts"
    )


class VendorProductClassDiscountFutureFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_discount: NullableStr = Field(default=None, alias="filter[discount]")
    filter_effective_date: NullableStr = Field(
        default=None, alias="filter[effective-date]"
    )


class VendorProductClassDiscountFutureFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_product_class_discounts: NullableStr = Field(
        default=None, alias="fields[vendor-product-class-discounts]"
    )
    fields_vendor_product_class_discounts_future: NullableStr = Field(
        default=None, alias="fields[vendor-product-class-discounts-future]"
    )


class VendorProductClassDiscountFutureRObj(VendorProductClassDiscountFutureRID):
    attributes: VendorProductClassDiscountFutureAttrs
    relationships: VendorProductClassDiscountFutureRels


class VendorProductClassDiscountFutureResp(JSONAPIResponse):
    data: (
        list[VendorProductClassDiscountFutureRObj]
        | VendorProductClassDiscountFutureRObj
    )


class RelatedVendorProductClassDiscountFutureResp(VendorProductClassDiscountFutureResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorProductClassDiscountFutureQuery: type[BaseModel] = create_model(
    "VendorProductClassDiscountFutureQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorProductClassDiscountFutureRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorProductClassDiscountFutureAttrs.model_fields.keys()
    },
    **{f"fields_vendor_product_class_discounts_future": (NullableStr, None)},
)


class VendorProductClassDiscountFutureQuery(
    _VendorProductClassDiscountFutureQuery, BaseModel
): ...


class VendorProductClassDiscountFutureQueryJSONAPI(
    VendorProductClassDiscountFutureFields,
    VendorProductClassDiscountFutureFilters,
    Query,
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorProductClassDiscountFutureAttrs(BaseModel):
    discount: NullableFloat = Field(default=None, alias="discount")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")


class ModVendorProductClassDiscountFutureRObj(BaseModel):
    id: int
    type: str = VendorProductClassDiscountFuture.__jsonapi_type_override__
    attributes: ModVendorProductClassDiscountFutureAttrs
    relationships: VendorProductClassDiscountFutureRels


class ModVendorProductClassDiscountFuture(BaseModel):
    data: ModVendorProductClassDiscountFutureRObj


class NewVendorProductClassDiscountFutureRObj(BaseModel):
    type: str = VendorProductClassDiscountFuture.__jsonapi_type_override__
    attributes: ModVendorProductClassDiscountFutureAttrs
    relationships: VendorProductClassDiscountFutureRels


class NewVendorProductClassDiscountFuture(BaseModel):
    data: NewVendorProductClassDiscountFutureRObj


from app.jsonapi.sqla_models import VendorPricingByCustomerFuture


class VendorPricingByCustomerFutureRID(JSONAPIResourceIdentifier):
    type: str = VendorPricingByCustomerFuture.__jsonapi_type_override__


class VendorPricingByCustomerFutureRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorPricingByCustomerFutureRID] | VendorPricingByCustomerFutureRID


class VendorPricingByCustomerFutureAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    price: NullableInt = Field(default=None, alias="price")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")


class VendorPricingByCustomerFutureRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_pricing_by_customer: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-pricing-by-customer"
    )


class VendorPricingByCustomerFutureFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_price: NullableStr = Field(default=None, alias="filter[price]")
    filter_effective_date: NullableStr = Field(
        default=None, alias="filter[effective-date]"
    )


class VendorPricingByCustomerFutureFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_by_customer: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )
    fields_vendor_pricing_by_customer_future: NullableStr = Field(
        default=None, alias="fields[vendor-pricing-by-customer-future]"
    )


class VendorPricingByCustomerFutureRObj(VendorPricingByCustomerFutureRID):
    attributes: VendorPricingByCustomerFutureAttrs
    relationships: VendorPricingByCustomerFutureRels


class VendorPricingByCustomerFutureResp(JSONAPIResponse):
    data: list[VendorPricingByCustomerFutureRObj] | VendorPricingByCustomerFutureRObj


class VendorPricingByCustomerFutureCollectionResp(JSONAPIResponse):
    data: list[VendorPricingByCustomerFutureRObj]


class VendorPricingByCustomerFutureResourceResp(JSONAPIResponse):
    data: VendorPricingByCustomerFutureRObj


class RelatedVendorPricingByCustomerFutureResp(VendorPricingByCustomerFutureResp):
    included: OptionalList
    links: OptionalDict = Field(exclude=True)


_VendorPricingByCustomerFutureQuery: type[BaseModel] = create_model(
    "VendorPricingByCustomerFutureQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorPricingByCustomerFutureRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorPricingByCustomerFutureAttrs.model_fields.keys()
    },
    **{f"fields_vendor_pricing_by_customer_future": (NullableStr, None)},
)


class VendorPricingByCustomerFutureQuery(
    _VendorPricingByCustomerFutureQuery, BaseModel
): ...


class VendorPricingByCustomerFutureQueryJSONAPI(
    VendorPricingByCustomerFutureFields, VendorPricingByCustomerFutureFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorPricingByCustomerFutureAttrs(BaseModel):
    price: NullableInt = Field(default=None, alias="price")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")


class ModVendorPricingByCustomerFutureRObj(BaseModel):
    id: int
    type: str = VendorPricingByCustomerFuture.__jsonapi_type_override__
    attributes: ModVendorPricingByCustomerFutureAttrs
    relationships: VendorPricingByCustomerFutureRels


class ModVendorPricingByCustomerFuture(BaseModel):
    data: ModVendorPricingByCustomerFutureRObj


class NewVendorPricingByCustomerFutureRObj(BaseModel):
    type: str = VendorPricingByCustomerFuture.__jsonapi_type_override__
    attributes: ModVendorPricingByCustomerFutureAttrs
    relationships: VendorPricingByCustomerFutureRels


class NewVendorPricingByCustomerFuture(BaseModel):
    data: NewVendorPricingByCustomerFutureRObj


from app.jsonapi.sqla_models import VendorProductDiscount


class VendorProductDiscountRID(JSONAPIResourceIdentifier):
    type: str = VendorProductDiscount.__jsonapi_type_override__


class VendorProductDiscountRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorProductDiscountRID]


class VendorProductDiscountAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    discount: NullableFloat = Field(default=None, alias="discount")
    effective_date: NullableDateTime = Field(default=None, alias="effective-date")
    deleted_at: NullableDateTime = Field(default=None, alias="deleted-at")


class VendorProductDiscountRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_products: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-products"
    )
    vendor_customers: OptionalJSONAPIRelationships = Field(
        default=None, alias="vendor-customers"
    )
    base_price_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="base-price-classes"
    )
    label_price_classes: OptionalJSONAPIRelationships = Field(
        default=None, alias="label-price-classes"
    )


class VendorProductDiscountFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_discount: str = Field(default=None, alias="filter[discount]")
    filter_effective_date: str = Field(default=None, alias="filter[effective-date]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorProductDiscountFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_products: str = Field(default=None, alias="fields[vendor-products]")
    fields_vendor_customers: str = Field(default=None, alias="fields[vendor-customers]")
    fields_base_price_classes: str = Field(
        default=None, alias="fields[base-price-classes]"
    )
    fields_label_price_classes: str = Field(
        default=None, alias="fields[label-price-classes]"
    )
    fields_vendor_product_discounts: str = Field(
        default=None, alias="fields[vendor-product-discounts]"
    )


class VendorProductDiscountRObj(VendorProductDiscountRID):
    attributes: VendorProductDiscountAttrs
    relationships: VendorProductDiscountRels


class VendorProductDiscountCollectionResp(JSONAPIResponse):
    data: list[VendorProductDiscountRObj]


class VendorProductDiscountResourceResp(JSONAPIResponse):
    data: VendorProductDiscountRObj


class RelatedVendorProductDiscountResp(VendorProductDiscountResourceResp):
    included: OptionalList = Field(default_factory=list)
    links: OptionalDict = Field(exclude=True)


_VendorProductDiscountQuery: type[BaseModel] = create_model(
    "VendorProductDiscountQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (NullableStr, None)
        for field in VendorProductDiscountRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (NullableStr, None)
        for field in VendorProductDiscountAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_product_discounts": (
            NullableStr,
            None,
        )
    },
)


class VendorProductDiscountQuery(_VendorProductDiscountQuery, BaseModel): ...


class VendorProductDiscountQueryJSONAPI(
    VendorProductDiscountFields, VendorProductDiscountFilters, Query
):
    page_number: NullableInt = Field(default=None, alias="page[number]")
    page_size: NullableInt = Field(default=None, alias="page[size]")


class ModVendorProductDiscountRObj(BaseModel):
    id: int
    type: str = VendorProductDiscount.__jsonapi_type_override__
    attributes: VendorProductDiscountAttrs
    relationships: VendorProductDiscountRels


class ModVendorProductDiscount(BaseModel):
    data: ModVendorProductDiscountRObj


class NewVendorProductDiscountRObj(BaseModel):
    type: str = VendorProductDiscount.__jsonapi_type_override__
    attributes: VendorProductDiscountAttrs
    relationships: VendorProductDiscountRels


class NewVendorProductDiscount(BaseModel):
    data: NewVendorProductDiscountRObj


converters = {
    VendorQuery: __convert_query(VendorQueryJSONAPI),
    VendorCustomerPricingClassQuery: __convert_query(
        VendorCustomerPricingClassQueryJSONAPI
    ),
    VendorPricingByClassChangelogQuery: __convert_query(
        VendorPricingByClassChangelogQueryJSONAPI
    ),
    VendorPricingByCustomerQuery: __convert_query(VendorPricingByCustomerQueryJSONAPI),
    VendorCustomerAttrQuery: __convert_query(VendorCustomerAttrQueryJSONAPI),
    VendorCustomerPricingClassesChangelogQuery: __convert_query(
        VendorCustomerPricingClassesChangelogQueryJSONAPI
    ),
    VendorQuoteChangelogQuery: __convert_query(VendorQuoteChangelogQueryJSONAPI),
    CustomerLocationMappingQuery: __convert_query(CustomerLocationMappingQueryJSONAPI),
    VendorPricingByCustomerAttrQuery: __convert_query(
        VendorPricingByCustomerAttrQueryJSONAPI
    ),
    VendorProductClassDiscountQuery: __convert_query(
        VendorProductClassDiscountQueryJSONAPI
    ),
    VendorCustomerQuery: __convert_query(VendorCustomerQueryJSONAPI),
    VendorProductQuery: __convert_query(VendorProductQueryJSONAPI),
    CustomerPricingByClassQuery: __convert_query(CustomerPricingByClassQueryJSONAPI),
    VendorQuoteAttrQuery: __convert_query(VendorQuoteAttrQueryJSONAPI),
    VendorsAttrQuery: __convert_query(VendorsAttrQueryJSONAPI),
    VendorCustomerAttrChangelogQuery: __convert_query(
        VendorCustomerAttrChangelogQueryJSONAPI
    ),
    VendorPricingByCustomerChangelogQuery: __convert_query(
        VendorPricingByCustomerChangelogQueryJSONAPI
    ),
    CustomerPricingByCustomerQuery: __convert_query(
        CustomerPricingByCustomerQueryJSONAPI
    ),
    VendorCustomerChangelogQuery: __convert_query(VendorCustomerChangelogQueryJSONAPI),
    VendorsAttrsChangelogQuery: __convert_query(VendorsAttrsChangelogQueryJSONAPI),
    VendorQuoteProductChangelogQuery: __convert_query(
        VendorQuoteProductChangelogQueryJSONAPI
    ),
    VendorQuoteProductQuery: __convert_query(VendorQuoteProductQueryJSONAPI),
    VendorProductClassQuery: __convert_query(VendorProductClassQueryJSONAPI),
    VendorProductAttrQuery: __convert_query(VendorProductAttrQueryJSONAPI),
    VendorProductClassDiscountsChangelogQuery: __convert_query(
        VendorProductClassDiscountsChangelogQueryJSONAPI
    ),
    VendorPricingClassQuery: __convert_query(VendorPricingClassQueryJSONAPI),
    VendorPricingByClassQuery: __convert_query(VendorPricingByClassQueryJSONAPI),
    VendorQuoteQuery: __convert_query(VendorQuoteQueryJSONAPI),
    VendorProductToClassMappingQuery: __convert_query(
        VendorProductToClassMappingQueryJSONAPI
    ),
    VendorProductClassDiscountFutureQuery: __convert_query(
        VendorProductClassDiscountFutureQueryJSONAPI
    ),
    VendorPricingByCustomerFutureQuery: __convert_query(
        VendorPricingByCustomerFutureQueryJSONAPI
    ),
    VendorProductDiscountQuery: __convert_query(VendorProductDiscountQueryJSONAPI),
}
