from pydantic import BaseModel, Field, create_model, ConfigDict
from typing import Optional
from datetime import datetime
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResponse,
    Query,
)

from app.jsonapi.sqla_models import Vendor


class VendorRID(JSONAPIResourceIdentifier):
    type: str = Vendor.__jsonapi_type_override__


class VendorRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorRID] | VendorRID


class VendorAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Optional[str] = Field(default=None, alias="name")
    headquarters: Optional[str] = Field(default=None, alias="headquarters")
    description: Optional[str] = Field(default=None, alias="description")
    phone: Optional[int] = Field(default=None, alias="phone")
    logo_path: Optional[str] = Field(default=None, alias="logo-path")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors_attrs: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors-attrs"
    )
    vendor_products: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-products"
    )
    vendor_product_classes: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-product-classes"
    )
    vendor_pricing_classes: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-classes"
    )
    vendor_customers: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customers"
    )


class VendorFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_name: str = Field(default=None, alias="filter[name]")
    filter_headquarters: str = Field(default=None, alias="filter[headquarters]")
    filter_description: str = Field(default=None, alias="filter[description]")
    filter_phone: str = Field(default=None, alias="filter[phone]")
    filter_logo_path: str = Field(default=None, alias="filter[logo-path]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors_attrs: str = Field(default=None, alias="fields[vendors-attrs]")
    fields_vendor_products: str = Field(default=None, alias="fields[vendor-products]")
    fields_vendor_product_classes: str = Field(
        default=None, alias="fields[vendor-product-classes]"
    )
    fields_vendor_pricing_classes: str = Field(
        default=None, alias="fields[vendor-pricing-classes]"
    )
    fields_vendor_customers: str = Field(default=None, alias="fields[vendor-customers]")
    fields_vendors: str = Field(default=None, alias="fields[vendors]")


class VendorRObj(VendorRID):
    attributes: VendorAttrs
    relationships: VendorRels


class VendorResp(JSONAPIResponse):
    data: list[VendorRObj] | VendorRObj


class RelatedVendorResp(VendorResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorQuery: type[BaseModel] = create_model(
    "VendorQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorAttrs.model_fields.keys()
    },
    **{
        f"fields_vendors": (
            Optional[str],
            None,
        )
    },
)


class VendorQuery(_VendorQuery, BaseModel): ...


class VendorQueryJSONAPI(VendorFields, VendorFilters, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorAttrs(BaseModel):
    name: Optional[str] = Field(default=None, alias="name")
    headquarters: Optional[str] = Field(default=None, alias="headquarters")
    description: Optional[str] = Field(default=None, alias="description")
    phone: Optional[int] = Field(default=None, alias="phone")
    logo_path: Optional[str] = Field(default=None, alias="logo-path")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class ModVendorRObj(BaseModel):
    id: int
    type: str = Vendor.__jsonapi_type_override__
    attributes: ModVendorAttrs
    relationships: VendorRels


class ModVendor(BaseModel):
    data: ModVendorRObj


from app.jsonapi.sqla_models import VendorsAttr


class VendorsAttrRID(JSONAPIResourceIdentifier):
    type: str = VendorsAttr.__jsonapi_type_override__


class VendorsAttrRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorsAttrRID] | VendorsAttrRID


class VendorsAttrAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    attr: Optional[str] = Field(default=None, alias="attr")
    type: Optional[str] = Field(default=None, alias="type")
    value: Optional[str] = Field(default=None, alias="value")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorsAttrRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: Optional[JSONAPIRelationships] = Field(default=None, alias="vendors")
    vendors_attrs_changelog: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors-attrs-changelog"
    )


class VendorsAttrFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_attr: str = Field(default=None, alias="filter[attr]")
    filter_type: str = Field(default=None, alias="filter[type]")
    filter_value: str = Field(default=None, alias="filter[value]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorsAttrFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors: str = Field(default=None, alias="fields[vendors]")
    fields_vendors_attrs_changelog: str = Field(
        default=None, alias="fields[vendors-attrs-changelog]"
    )
    fields_vendors_attrs: str = Field(default=None, alias="fields[vendors-attrs]")


class VendorsAttrRObj(VendorsAttrRID):
    attributes: VendorsAttrAttrs
    relationships: VendorsAttrRels


class VendorsAttrResp(JSONAPIResponse):
    data: list[VendorsAttrRObj] | VendorsAttrRObj


class RelatedVendorsAttrResp(VendorsAttrResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorsAttrQuery: type[BaseModel] = create_model(
    "VendorsAttrQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorsAttrRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorsAttrAttrs.model_fields.keys()
    },
    **{
        f"fields_vendors_attrs": (
            Optional[str],
            None,
        )
    },
)


class VendorsAttrQuery(_VendorsAttrQuery, BaseModel): ...


class VendorsAttrQueryJSONAPI(VendorsAttrFields, VendorsAttrFilters, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorsAttrAttrs(BaseModel):
    value: Optional[str] = Field(default=None, alias="value")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


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
    data: list[VendorProductRID] | VendorProductRID


class VendorProductAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_product_identifier: Optional[str] = Field(
        default=None, alias="vendor-product-identifier"
    )
    vendor_product_description: Optional[str] = Field(
        default=None, alias="vendor-product-description"
    )
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorProductRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: Optional[JSONAPIRelationships] = Field(default=None, alias="vendors")
    vendor_pricing_by_class: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-by-class"
    )
    vendor_pricing_by_customer: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-by-customer"
    )
    vendor_product_attrs: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-product-attrs"
    )
    vendor_product_to_class_mapping: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-product-to-class-mapping"
    )
    vendor_quote_products: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-quote-products"
    )


class VendorProductFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_vendor_product_identifier: str = Field(
        default=None, alias="filter[vendor-product-identifier]"
    )
    filter_vendor_product_description: str = Field(
        default=None, alias="filter[vendor-product-description]"
    )
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorProductFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors: str = Field(default=None, alias="fields[vendors]")
    fields_vendor_pricing_by_class: str = Field(
        default=None, alias="fields[vendor-pricing-by-class]"
    )
    fields_vendor_pricing_by_customer: str = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )
    fields_vendor_product_attrs: str = Field(
        default=None, alias="fields[vendor-product-attrs]"
    )
    fields_vendor_product_to_class_mapping: str = Field(
        default=None, alias="fields[vendor-product-to-class-mapping]"
    )
    fields_vendor_quote_products: str = Field(
        default=None, alias="fields[vendor-quote-products]"
    )
    fields_vendor_products: str = Field(default=None, alias="fields[vendor-products]")


class VendorProductRObj(VendorProductRID):
    attributes: VendorProductAttrs
    relationships: VendorProductRels


class VendorProductResp(JSONAPIResponse):
    data: list[VendorProductRObj] | VendorProductRObj


class RelatedVendorProductResp(VendorProductResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorProductQuery: type[BaseModel] = create_model(
    "VendorProductQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorProductRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorProductAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_products": (
            Optional[str],
            None,
        )
    },
)


class VendorProductQuery(_VendorProductQuery, BaseModel): ...


class VendorProductQueryJSONAPI(VendorProductFields, VendorProductFilters, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorProductAttrs(BaseModel):
    vendor_product_description: Optional[str] = Field(
        default=None, alias="vendor-product-description"
    )
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


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
    attr: Optional[str] = Field(default=None, alias="attr")
    type: Optional[str] = Field(default=None, alias="type")
    value: Optional[str] = Field(default=None, alias="value")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorProductAttrRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_products: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-products"
    )


class VendorProductAttrFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_attr: str = Field(default=None, alias="filter[attr]")
    filter_type: str = Field(default=None, alias="filter[type]")
    filter_value: str = Field(default=None, alias="filter[value]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorProductAttrFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_products: str = Field(default=None, alias="fields[vendor-products]")
    fields_vendor_product_attrs: str = Field(
        default=None, alias="fields[vendor-product-attrs]"
    )


class VendorProductAttrRObj(VendorProductAttrRID):
    attributes: VendorProductAttrAttrs
    relationships: VendorProductAttrRels


class VendorProductAttrResp(JSONAPIResponse):
    data: list[VendorProductAttrRObj] | VendorProductAttrRObj


class RelatedVendorProductAttrResp(VendorProductAttrResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorProductAttrQuery: type[BaseModel] = create_model(
    "VendorProductAttrQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorProductAttrRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorProductAttrAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_product_attrs": (
            Optional[str],
            None,
        )
    },
)


class VendorProductAttrQuery(_VendorProductAttrQuery, BaseModel): ...


class VendorProductAttrQueryJSONAPI(
    VendorProductAttrFields, VendorProductAttrFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorProductAttrAttrs(BaseModel):
    value: Optional[str] = Field(default=None, alias="value")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


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
    data: list[VendorProductClassRID] | VendorProductClassRID


class VendorProductClassAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Optional[str] = Field(default=None, alias="name")
    rank: Optional[int] = Field(default=None, alias="rank")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorProductClassRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: Optional[JSONAPIRelationships] = Field(default=None, alias="vendors")
    vendor_product_to_class_mapping: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-product-to-class-mapping"
    )
    vendor_product_class_discounts: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-product-class-discounts"
    )


class VendorProductClassFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_name: str = Field(default=None, alias="filter[name]")
    filter_rank: str = Field(default=None, alias="filter[rank]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorProductClassFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors: str = Field(default=None, alias="fields[vendors]")
    fields_vendor_product_to_class_mapping: str = Field(
        default=None, alias="fields[vendor-product-to-class-mapping]"
    )
    fields_vendor_product_class_discounts: str = Field(
        default=None, alias="fields[vendor-product-class-discounts]"
    )
    fields_vendor_product_classes: str = Field(
        default=None, alias="fields[vendor-product-classes]"
    )


class VendorProductClassRObj(VendorProductClassRID):
    attributes: VendorProductClassAttrs
    relationships: VendorProductClassRels


class VendorProductClassResp(JSONAPIResponse):
    data: list[VendorProductClassRObj] | VendorProductClassRObj


class RelatedVendorProductClassResp(VendorProductClassResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorProductClassQuery: type[BaseModel] = create_model(
    "VendorProductClassQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorProductClassRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorProductClassAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_product_classes": (
            Optional[str],
            None,
        )
    },
)


class VendorProductClassQuery(_VendorProductClassQuery, BaseModel): ...


class VendorProductClassQueryJSONAPI(
    VendorProductClassFields, VendorProductClassFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorProductClassAttrs(BaseModel):
    name: Optional[str] = Field(default=None, alias="name")
    rank: Optional[int] = Field(default=None, alias="rank")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


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
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorProductToClassMappingRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_product_classes: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-product-classes"
    )
    vendor_products: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-products"
    )


class VendorProductToClassMappingFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorProductToClassMappingFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_product_classes: str = Field(
        default=None, alias="fields[vendor-product-classes]"
    )
    fields_vendor_products: str = Field(default=None, alias="fields[vendor-products]")
    fields_vendor_product_to_class_mapping: str = Field(
        default=None, alias="fields[vendor-product-to-class-mapping]"
    )


class VendorProductToClassMappingRObj(VendorProductToClassMappingRID):
    attributes: VendorProductToClassMappingAttrs
    relationships: VendorProductToClassMappingRels


class VendorProductToClassMappingResp(JSONAPIResponse):
    data: list[VendorProductToClassMappingRObj] | VendorProductToClassMappingRObj


class RelatedVendorProductToClassMappingResp(VendorProductToClassMappingResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorProductToClassMappingQuery: type[BaseModel] = create_model(
    "VendorProductToClassMappingQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorProductToClassMappingRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorProductToClassMappingAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_product_to_class_mapping": (
            Optional[str],
            None,
        )
    },
)


class VendorProductToClassMappingQuery(
    _VendorProductToClassMappingQuery, BaseModel
): ...


class VendorProductToClassMappingQueryJSONAPI(
    VendorProductToClassMappingFields, VendorProductToClassMappingFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorProductToClassMappingAttrs(BaseModel):
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class ModVendorProductToClassMappingRObj(BaseModel):
    id: int
    type: str = VendorProductToClassMapping.__jsonapi_type_override__
    attributes: ModVendorProductToClassMappingAttrs
    relationships: VendorProductToClassMappingRels


class ModVendorProductToClassMapping(BaseModel):
    data: ModVendorProductToClassMappingRObj
