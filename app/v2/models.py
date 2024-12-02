from pydantic import BaseModel, Field, create_model, ConfigDict
from typing import Optional
from datetime import datetime
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResponse,
    Query,
    convert_query as __convert_query,
)
from app.db import Stage

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
    id: str
    type: str = Vendor.__jsonapi_type_override__
    attributes: ModVendorAttrs
    relationships: Optional[VendorRels] = None


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


class NewVendorsAttrRObj(BaseModel):
    type: str = VendorsAttr.__jsonapi_type_override__
    attributes: VendorsAttrAttrs
    relationships: VendorsAttrRels


class NewVendorsAttr(BaseModel):
    data: NewVendorsAttrRObj


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
    vendors: JSONAPIRelationships = Field(default=None, alias="vendors")
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


class NewVendorProductRObj(BaseModel):
    type: str = VendorProduct.__jsonapi_type_override__
    attributes: VendorProductAttrs
    relationships: VendorProductRels


class NewVendorProduct(BaseModel):
    data: NewVendorProductRObj


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
    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
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


class NewVendorProductAttrRObj(BaseModel):
    type: str = VendorProductAttr.__jsonapi_type_override__
    attributes: VendorProductAttrAttrs
    relationships: VendorProductAttrRels


class NewVendorProductAttr(BaseModel):
    data: NewVendorProductAttrRObj


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


class NewVendorProductClassRObj(BaseModel):
    type: str = VendorProductClass.__jsonapi_type_override__
    attributes: VendorProductClassAttrs
    relationships: VendorProductClassRels


class NewVendorProductClass(BaseModel):
    data: NewVendorProductClassRObj


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
    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
    )
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


class NewVendorProductToClassMappingRObj(BaseModel):
    type: str = VendorProductToClassMapping.__jsonapi_type_override__
    attributes: Optional[VendorProductToClassMappingAttrs] = Field(default=None)
    relationships: VendorProductToClassMappingRels


class NewVendorProductToClassMapping(BaseModel):
    data: NewVendorProductToClassMappingRObj


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


from app.jsonapi.sqla_models import VendorPricingClass


class VendorPricingClassRID(JSONAPIResourceIdentifier):
    type: str = VendorPricingClass.__jsonapi_type_override__


class VendorPricingClassRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorPricingClassRID] | VendorPricingClassRID


class VendorPricingClassAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Optional[str] = Field(default=None, alias="name")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorPricingClassRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: Optional[JSONAPIRelationships] = Field(default=None, alias="vendors")
    vendor_pricing_by_class: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-by-class"
    )
    vendor_pricing_by_customer: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-by-customer"
    )
    vendor_customer_pricing_classes: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customer-pricing-classes"
    )
    vendor_customer_pricing_classes_changelog: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customer-pricing-classes-changelog"
    )


class VendorPricingClassFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_name: str = Field(default=None, alias="filter[name]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorPricingClassFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors: str = Field(default=None, alias="fields[vendors]")
    fields_vendor_pricing_by_class: str = Field(
        default=None, alias="fields[vendor-pricing-by-class]"
    )
    fields_vendor_pricing_by_customer: str = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )
    fields_vendor_customer_pricing_classes: str = Field(
        default=None, alias="fields[vendor-customer-pricing-classes]"
    )
    fields_vendor_customer_pricing_classes_changelog: str = Field(
        default=None, alias="fields[vendor-customer-pricing-classes-changelog]"
    )
    fields_vendor_pricing_classes: str = Field(
        default=None, alias="fields[vendor-pricing-classes]"
    )


class VendorPricingClassRObj(VendorPricingClassRID):
    attributes: VendorPricingClassAttrs
    relationships: VendorPricingClassRels


class VendorPricingClassResp(JSONAPIResponse):
    data: list[VendorPricingClassRObj] | VendorPricingClassRObj


class NewVendorPricingClassRObj(BaseModel):
    type: str = VendorPricingClass.__jsonapi_type_override__
    attributes: VendorPricingClassAttrs
    relationships: VendorPricingClassRels


class NewVendorPricingClass(BaseModel):
    data: NewVendorPricingClassRObj


class RelatedVendorPricingClassResp(VendorPricingClassResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorPricingClassQuery: type[BaseModel] = create_model(
    "VendorPricingClassQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorPricingClassRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorPricingClassAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_pricing_classes": (
            Optional[str],
            None,
        )
    },
)


class VendorPricingClassQuery(_VendorPricingClassQuery, BaseModel): ...


class VendorPricingClassQueryJSONAPI(
    VendorPricingClassFields, VendorPricingClassFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorPricingClassAttrs(BaseModel):
    name: Optional[str] = Field(default=None, alias="name")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


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
    price: Optional[int] = Field(default=None, alias="price")
    effective_date: Optional[datetime] = Field(default=None, alias="effective-date")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorPricingByClassRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_pricing_classes: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-classes"
    )
    vendor_products: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-products"
    )
    vendor_pricing_by_class_changelog: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-by-class-changelog"
    )
    customer_pricing_by_class: Optional[JSONAPIRelationships] = Field(
        default=None, alias="customer-pricing-by-class"
    )


class VendorPricingByClassFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_price: str = Field(default=None, alias="filter[price]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorPricingByClassFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_classes: str = Field(
        default=None, alias="fields[vendor-pricing-classes]"
    )
    fields_vendor_products: str = Field(default=None, alias="fields[vendor-products]")
    fields_vendor_pricing_by_class_changelog: str = Field(
        default=None, alias="fields[vendor-pricing-by-class-changelog]"
    )
    fields_customer_pricing_by_class: str = Field(
        default=None, alias="fields[customer-pricing-by-class]"
    )
    fields_vendor_pricing_by_class: str = Field(
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
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorPricingByClassQuery: type[BaseModel] = create_model(
    "VendorPricingByClassQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorPricingByClassRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorPricingByClassAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_pricing_by_class": (
            Optional[str],
            None,
        )
    },
)


class VendorPricingByClassQuery(_VendorPricingByClassQuery, BaseModel): ...


class VendorPricingByClassQueryJSONAPI(
    VendorPricingByClassFields, VendorPricingByClassFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorPricingByClassAttrs(BaseModel):
    price: Optional[int] = Field(default=None, alias="price")
    effective_date: Optional[datetime] = Field(default=None, alias="effective-date")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


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
    data: list[VendorPricingByClassChangelogRID] | VendorPricingByClassChangelogRID


class VendorPricingByClassChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    price: Optional[int] = Field(default=None, alias="price")
    effective_date: Optional[datetime] = Field(default=None, alias="effective-date")
    timestamp: Optional[datetime] = Field(default=None, alias="timestamp")


class VendorPricingByClassChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_pricing_by_class: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-by-class"
    )


class VendorPricingByClassChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_price: str = Field(default=None, alias="filter[price]")
    filter_timestamp: str = Field(default=None, alias="filter[timestamp]")


class VendorPricingByClassChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_by_class: str = Field(
        default=None, alias="fields[vendor-pricing-by-class]"
    )
    fields_vendor_pricing_by_class_changelog: str = Field(
        default=None, alias="fields[vendor-pricing-by-class-changelog]"
    )


class VendorPricingByClassChangelogRObj(VendorPricingByClassChangelogRID):
    attributes: VendorPricingByClassChangelogAttrs
    relationships: VendorPricingByClassChangelogRels


class VendorPricingByClassChangelogResp(JSONAPIResponse):
    data: list[VendorPricingByClassChangelogRObj] | VendorPricingByClassChangelogRObj


class RelatedVendorPricingByClassChangelogResp(VendorPricingByClassChangelogResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorPricingByClassChangelogQuery: type[BaseModel] = create_model(
    "VendorPricingByClassChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorPricingByClassChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorPricingByClassChangelogAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_pricing_by_class_changelog": (
            Optional[str],
            None,
        )
    },
)


class VendorPricingByClassChangelogQuery(
    _VendorPricingByClassChangelogQuery, BaseModel
): ...


class VendorPricingByClassChangelogQueryJSONAPI(
    VendorPricingByClassChangelogFields, VendorPricingByClassChangelogFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorPricingByCustomer


class VendorPricingByCustomerRID(JSONAPIResourceIdentifier):
    type: str = VendorPricingByCustomer.__jsonapi_type_override__


class VendorPricingByCustomerRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorPricingByCustomerRID] | VendorPricingByCustomerRID


class VendorPricingByCustomerAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    use_as_override: Optional[bool] = Field(default=None, alias="use-as-override")
    price: Optional[int] = Field(default=None, alias="price")
    effective_date: Optional[datetime] = Field(default=None, alias="effective-date")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorPricingByCustomerRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_customers: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customers"
    )
    vendor_products: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-products"
    )
    vendor_pricing_by_customer_attrs: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-by-customer-attrs"
    )
    vendor_pricing_classes: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-classes"
    )
    vendor_pricing_by_customer_changelog: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-by-customer-changelog"
    )
    customer_pricing_by_customer: Optional[JSONAPIRelationships] = Field(
        default=None, alias="customer-pricing-by-customer"
    )
    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
    )


class VendorPricingByCustomerFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_use_as_override: str = Field(default=None, alias="filter[use-as-override]")
    filter_price: str = Field(default=None, alias="filter[price]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorPricingByCustomerFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customers: str = Field(default=None, alias="fields[vendor-customers]")
    fields_vendor_products: str = Field(default=None, alias="fields[vendor-products]")
    fields_vendor_pricing_by_customer_attrs: str = Field(
        default=None, alias="fields[vendor-pricing-by-customer-attrs]"
    )
    fields_vendor_pricing_classes: str = Field(
        default=None, alias="fields[vendor-pricing-classes]"
    )
    fields_vendor_pricing_by_customer_changelog: str = Field(
        default=None, alias="fields[vendor-pricing-by-customer-changelog]"
    )
    fields_customer_pricing_by_customer: str = Field(
        default=None, alias="fields[customer-pricing-by-customer]"
    )
    fields_vendor_pricing_by_customer: str = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )


class VendorPricingByCustomerRObj(VendorPricingByCustomerRID):
    attributes: VendorPricingByCustomerAttrs
    relationships: VendorPricingByCustomerRels


class VendorPricingByCustomerResp(JSONAPIResponse):
    data: list[VendorPricingByCustomerRObj] | VendorPricingByCustomerRObj


class NewVendorPricingByCustomerRObj(BaseModel):
    type: str = VendorPricingByCustomer.__jsonapi_type_override__
    attributes: VendorPricingByCustomerAttrs
    relationships: VendorPricingByCustomerRels


class NewVendorPricingByCustomer(BaseModel):
    data: NewVendorPricingByCustomerRObj


class RelatedVendorPricingByCustomerResp(VendorPricingByCustomerResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorPricingByCustomerQuery: type[BaseModel] = create_model(
    "VendorPricingByCustomerQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorPricingByCustomerRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorPricingByCustomerAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_pricing_by_customer": (
            Optional[str],
            None,
        )
    },
)


class VendorPricingByCustomerQuery(_VendorPricingByCustomerQuery, BaseModel): ...


class VendorPricingByCustomerQueryJSONAPI(
    VendorPricingByCustomerFields, VendorPricingByCustomerFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorPricingByCustomerAttrs(BaseModel):
    use_as_override: Optional[bool] = Field(default=None, alias="use-as-override")
    price: Optional[int] = Field(default=None, alias="price")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class ModVendorPricingByCustomerRObj(BaseModel):
    id: int
    type: str = VendorPricingByCustomer.__jsonapi_type_override__
    attributes: ModVendorPricingByCustomerAttrs
    relationships: VendorPricingByCustomerRels


class ModVendorPricingByCustomer(BaseModel):
    data: ModVendorPricingByCustomerRObj


from app.jsonapi.sqla_models import VendorCustomer


class VendorCustomerRID(JSONAPIResourceIdentifier):
    type: str = VendorCustomer.__jsonapi_type_override__


class VendorCustomerRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorCustomerRID] | VendorCustomerRID


class VendorCustomerAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Optional[str] = Field(default=None, alias="name")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorCustomerRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: Optional[JSONAPIRelationships] = Field(default=None, alias="vendors")
    vendor_pricing_by_customer: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-by-customer"
    )
    vendor_customer_pricing_classes_changelog: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customer-pricing-classes-changelog"
    )
    vendor_customer_pricing_classes: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customer-pricing-classes"
    )
    vendor_customer_changelog: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customer-changelog"
    )
    vendor_quotes: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-quotes"
    )
    vendor_customer_attrs: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customer-attrs"
    )
    vendor_product_class_discounts: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-product-class-discounts"
    )
    customer_location_mapping: Optional[JSONAPIRelationships] = Field(
        default=None, alias="customer-location-mapping"
    )


class VendorCustomerFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_name: str = Field(default=None, alias="filter[name]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")
    filter_vendor_product_classes__name: str = Field(
        default=None, alias="filter[vendor-product-classes.name]"
    )
    filter_vendor_product_classes__rank: str = Field(
        default=None, alias="filter[vendor-product-classes.rank]"
    )


class VendorCustomerFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors: str = Field(default=None, alias="fields[vendors]")
    fields_vendor_pricing_by_customer: str = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )
    fields_vendor_customer_pricing_classes_changelog: str = Field(
        default=None, alias="fields[vendor-customer-pricing-classes-changelog]"
    )
    fields_vendor_customer_pricing_classes: str = Field(
        default=None, alias="fields[vendor-customer-pricing-classes]"
    )
    fields_vendor_customer_changelog: str = Field(
        default=None, alias="fields[vendor-customer-changelog]"
    )
    fields_vendor_quotes: str = Field(default=None, alias="fields[vendor-quotes]")
    fields_vendor_customer_attrs: str = Field(
        default=None, alias="fields[vendor-customer-attrs]"
    )
    fields_vendor_product_class_discounts: str = Field(
        default=None, alias="fields[vendor-product-class-discounts]"
    )
    fields_customer_location_mapping: str = Field(
        default=None, alias="fields[customer-location-mapping]"
    )
    fields_vendor_customers: str = Field(default=None, alias="fields[vendor-customers]")


class VendorCustomerRObj(VendorCustomerRID):
    attributes: VendorCustomerAttrs
    relationships: VendorCustomerRels


class VendorCustomerResp(JSONAPIResponse):
    data: list[VendorCustomerRObj] | VendorCustomerRObj


class NewVendorCustomerRObj(BaseModel):
    type: str = VendorCustomer.__jsonapi_type_override__
    attributes: VendorCustomerAttrs
    relationships: VendorCustomerRels


class NewVendorCustomer(BaseModel):
    data: NewVendorCustomerRObj


class RelatedVendorCustomerResp(VendorCustomerResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


vendor_customer_field_and_filter_params = (
    *VendorCustomerFields.model_fields.keys(),
    *VendorCustomerFilters.model_fields.keys(),
)
standard_query_params = {
    field: (field_info.annotation, field_info)
    for field, field_info in Query.model_fields.items()
}
vendor_customer_query_params = {
    field: (Optional[str], None) for field in vendor_customer_field_and_filter_params
}

_VendorCustomerQuery: type[BaseModel] = create_model(
    "VendorCustomerQuery", **standard_query_params, **vendor_customer_query_params
)


class VendorCustomerQuery(_VendorCustomerQuery, BaseModel): ...


class VendorCustomerQueryJSONAPI(VendorCustomerFields, VendorCustomerFilters, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorCustomerAttrs(BaseModel):
    name: Optional[str] = Field(default=None, alias="name")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


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
    price: Optional[int] = Field(default=None, alias="price")
    effective_date: Optional[datetime] = Field(default=None, alias="effective-date")
    timestamp: Optional[datetime] = Field(default=None, alias="timestamp")


class VendorPricingByCustomerChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_pricing_by_customer: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-by-customer"
    )


class VendorPricingByCustomerChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_price: str = Field(default=None, alias="filter[price]")
    filter_timestamp: str = Field(default=None, alias="filter[timestamp]")


class VendorPricingByCustomerChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_by_customer: str = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )
    fields_vendor_pricing_by_customer_changelog: str = Field(
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
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorPricingByCustomerChangelogQuery: type[BaseModel] = create_model(
    "VendorPricingByCustomerChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorPricingByCustomerChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorPricingByCustomerChangelogAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_pricing_by_customer_changelog": (
            Optional[str],
            None,
        )
    },
)


class VendorPricingByCustomerChangelogQuery(
    _VendorPricingByCustomerChangelogQuery, BaseModel
): ...


class VendorPricingByCustomerChangelogQueryJSONAPI(
    VendorPricingByCustomerChangelogFields,
    VendorPricingByCustomerChangelogFilters,
    Query,
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorProductClassDiscount


class VendorProductClassDiscountRID(JSONAPIResourceIdentifier):
    type: str = VendorProductClassDiscount.__jsonapi_type_override__


class VendorProductClassDiscountRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorProductClassDiscountRID] | VendorProductClassDiscountRID


class VendorProductClassDiscountAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    discount: Optional[float] = Field(default=None, alias="discount")
    effective_date: Optional[datetime] = Field(default=None, alias="effective-date")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorProductClassDiscountRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_customers: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customers"
    )
    vendor_product_classes: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-product-classes"
    )
    vendor_product_class_discounts_changelog: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-product-class-discounts-changelog"
    )


class VendorProductClassDiscountFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_discount: str = Field(default=None, alias="filter[discount]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorProductClassDiscountFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customers: str = Field(default=None, alias="fields[vendor-customers]")
    fields_vendor_product_classes: str = Field(
        default=None, alias="fields[vendor-product-classes]"
    )
    fields_vendor_product_class_discounts_changelog: str = Field(
        default=None, alias="fields[vendor-product-class-discounts-changelog]"
    )
    fields_vendor_product_class_discounts: str = Field(
        default=None, alias="fields[vendor-product-class-discounts]"
    )


class VendorProductClassDiscountRObj(VendorProductClassDiscountRID):
    attributes: VendorProductClassDiscountAttrs
    relationships: VendorProductClassDiscountRels


class VendorProductClassDiscountResp(JSONAPIResponse):
    data: list[VendorProductClassDiscountRObj] | VendorProductClassDiscountRObj


class NewVendorProductClassDiscountRObj(BaseModel):
    type: str = VendorProductClassDiscount.__jsonapi_type_override__
    attributes: VendorProductClassDiscountAttrs
    relationships: VendorProductClassDiscountRels


class NewVendorProductClassDiscount(BaseModel):
    data: NewVendorProductClassDiscountRObj


class RelatedVendorProductClassDiscountResp(VendorProductClassDiscountResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorProductClassDiscountQuery: type[BaseModel] = create_model(
    "VendorProductClassDiscountQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorProductClassDiscountRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorProductClassDiscountAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_product_class_discounts": (
            Optional[str],
            None,
        )
    },
)


class VendorProductClassDiscountQuery(_VendorProductClassDiscountQuery, BaseModel): ...


class VendorProductClassDiscountQueryJSONAPI(
    VendorProductClassDiscountFields, VendorProductClassDiscountFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorProductClassDiscountAttrs(BaseModel):
    discount: Optional[float] = Field(default=None, alias="discount")
    effective_date: Optional[datetime] = Field(default=None, alias="effective-date")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class ModVendorProductClassDiscountRObj(BaseModel):
    id: int
    type: str = VendorProductClassDiscount.__jsonapi_type_override__
    attributes: ModVendorProductClassDiscountAttrs
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
    attr: Optional[str] = Field(default=None, alias="attr")
    type: Optional[str] = Field(default=None, alias="type")
    value: Optional[str] = Field(default=None, alias="value")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorPricingByCustomerAttrRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_pricing_by_customer: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-by-customer"
    )


class VendorPricingByCustomerAttrFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_attr: str = Field(default=None, alias="filter[attr]")
    filter_type: str = Field(default=None, alias="filter[type]")
    filter_value: str = Field(default=None, alias="filter[value]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorPricingByCustomerAttrFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_by_customer: str = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )
    fields_vendor_pricing_by_customer_attrs: str = Field(
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
    value: Optional[str] = Field(default=None, alias="value")
    effective_date: Optional[datetime] = Field(default=None, alias="effective-date")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class ModVendorPricingByCustomerAttrRObj(BaseModel):
    id: int
    type: str = VendorPricingByCustomerAttr.__jsonapi_type_override__
    attributes: ModVendorPricingByCustomerAttrAttrs
    relationships: VendorPricingByCustomerAttrRels


class ModVendorPricingByCustomerAttr(BaseModel):
    data: ModVendorPricingByCustomerAttrRObj


class RelatedVendorPricingByCustomerAttrResp(VendorPricingByCustomerAttrResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorPricingByCustomerAttrQuery: type[BaseModel] = create_model(
    "VendorPricingByCustomerAttrQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorPricingByCustomerAttrRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorPricingByCustomerAttrAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_pricing_by_customer_attrs": (
            Optional[str],
            None,
        )
    },
)


class VendorPricingByCustomerAttrQuery(
    _VendorPricingByCustomerAttrQuery, BaseModel
): ...


class VendorPricingByCustomerAttrQueryJSONAPI(
    VendorPricingByCustomerAttrFields, VendorPricingByCustomerAttrFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


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
    discount: Optional[float] = Field(default=None, alias="discount")
    effective_date: Optional[datetime] = Field(default=None, alias="effective-date")
    timestamp: Optional[datetime] = Field(default=None, alias="timestamp")


class VendorProductClassDiscountsChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_product_class_discounts: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-product-class-discounts"
    )


class VendorProductClassDiscountsChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_discount: str = Field(default=None, alias="filter[discount]")
    filter_timestamp: str = Field(default=None, alias="filter[timestamp]")


class VendorProductClassDiscountsChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_product_class_discounts: str = Field(
        default=None, alias="fields[vendor-product-class-discounts]"
    )
    fields_vendor_product_class_discounts_changelog: str = Field(
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
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorProductClassDiscountsChangelogQuery: type[BaseModel] = create_model(
    "VendorProductClassDiscountsChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorProductClassDiscountsChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorProductClassDiscountsChangelogAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_product_class_discounts_changelog": (
            Optional[str],
            None,
        )
    },
)


class VendorProductClassDiscountsChangelogQuery(
    _VendorProductClassDiscountsChangelogQuery, BaseModel
): ...


class VendorProductClassDiscountsChangelogQueryJSONAPI(
    VendorProductClassDiscountsChangelogFields,
    VendorProductClassDiscountsChangelogFilters,
    Query,
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorQuote


class VendorQuoteRID(JSONAPIResourceIdentifier):
    type: str = VendorQuote.__jsonapi_type_override__


class VendorQuoteRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorQuoteRID] | VendorQuoteRID


class VendorQuoteAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_quote_number: Optional[str] = Field(
        default=None, alias="vendor-quote-number"
    )
    job_name: Optional[str] = Field(default=None, alias="job-name")
    status: Optional[Stage] = Field(default=None, alias="status")
    quote_doc: Optional[str] = Field(default=None, alias="quote-doc")
    plans_doc: Optional[str] = Field(default=None, alias="plans-doc")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorQuoteRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_customers: JSONAPIRelationships = Field(alias="vendor-customers")
    vendor_quote_products: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-quote-products"
    )
    places: Optional[JSONAPIRelationships] = Field(default=None, alias="places")
    vendor_quotes_changelog: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-quotes-changelog"
    )
    vendor_quotes_attrs: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-quotes-attrs"
    )
    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
    )


class VendorQuoteFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_vendor_quote_number: str = Field(
        default=None, alias="filter[vendor-quote-number]"
    )
    filter_job_name: str = Field(default=None, alias="filter[job-name]")
    filter_status: str = Field(default=None, alias="filter[status]")
    filter_quote_doc: str = Field(default=None, alias="filter[quote-doc]")
    filter_plans_doc: str = Field(default=None, alias="filter[plans-doc]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorQuoteFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customers: str = Field(default=None, alias="fields[vendor-customers]")
    fields_vendor_quote_products: str = Field(
        default=None, alias="fields[vendor-quote-products]"
    )
    fields_places: str = Field(default=None, alias="fields[places]")
    fields_vendor_quotes_changelog: str = Field(
        default=None, alias="fields[vendor-quotes-changelog]"
    )
    fields_vendor_quotes_attrs: str = Field(
        default=None, alias="fields[vendor-quotes-attrs]"
    )
    fields_vendor_quotes: str = Field(default=None, alias="fields[vendor-quotes]")


class VendorQuoteRObj(VendorQuoteRID):
    attributes: VendorQuoteAttrs
    relationships: VendorQuoteRels


class VendorQuoteResp(JSONAPIResponse):
    data: list[VendorQuoteRObj] | VendorQuoteRObj


class NewVendorQuoteRObj(BaseModel):
    type: str = VendorQuote.__jsonapi_type_override__
    attributes: VendorQuoteAttrs
    relationships: VendorQuoteRels


class NewVendorQuote(BaseModel):
    data: NewVendorQuoteRObj


class RelatedVendorQuoteResp(VendorQuoteResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorQuoteQuery: type[BaseModel] = create_model(
    "VendorQuoteQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorQuoteRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorQuoteAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_quotes": (
            Optional[str],
            None,
        )
    },
)


class VendorQuoteQuery(_VendorQuoteQuery, BaseModel): ...


class VendorQuoteQueryJSONAPI(VendorQuoteFields, VendorQuoteFilters, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorQuoteAttrs(BaseModel):
    vendor_quote_number: Optional[str] = Field(
        default=None, alias="vendor-quote-number"
    )
    status: Optional[Stage] = Field(default=None, alias="status")
    quote_doc: Optional[str] = Field(default=None, alias="quote-doc")
    plans_doc: Optional[str] = Field(default=None, alias="plans-doc")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


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
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class CustomerLocationMappingRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_customers: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customers"
    )
    customer_locations: Optional[JSONAPIRelationships] = Field(
        default=None, alias="customer-locations"
    )


class CustomerLocationMappingFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class CustomerLocationMappingFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customers: str = Field(default=None, alias="fields[vendor-customers]")
    fields_customer_locations: str = Field(
        default=None, alias="fields[customer-locations]"
    )
    fields_customer_location_mapping: str = Field(
        default=None, alias="fields[customer-location-mapping]"
    )


class CustomerLocationMappingRObj(CustomerLocationMappingRID):
    attributes: CustomerLocationMappingAttrs
    relationships: CustomerLocationMappingRels


class CustomerLocationMappingResp(JSONAPIResponse):
    data: list[CustomerLocationMappingRObj] | CustomerLocationMappingRObj


class NewCustomerLocationMappingRObj(BaseModel):
    type: str = CustomerLocationMapping.__jsonapi_type_override__
    attributes: Optional[CustomerLocationMappingAttrs] = Field(default=None)
    relationships: CustomerLocationMappingRels


class NewCustomerLocationMapping(BaseModel):
    data: NewCustomerLocationMappingRObj


class RelatedCustomerLocationMappingResp(CustomerLocationMappingResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_CustomerLocationMappingQuery: type[BaseModel] = create_model(
    "CustomerLocationMappingQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in CustomerLocationMappingRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in CustomerLocationMappingAttrs.model_fields.keys()
    },
    **{
        f"fields_customer_location_mapping": (
            Optional[str],
            None,
        )
    },
)


class CustomerLocationMappingQuery(_CustomerLocationMappingQuery, BaseModel): ...


class CustomerLocationMappingQueryJSONAPI(
    CustomerLocationMappingFields, CustomerLocationMappingFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorQuoteProduct


class VendorQuoteProductRID(JSONAPIResourceIdentifier):
    type: str = VendorQuoteProduct.__jsonapi_type_override__


class VendorQuoteProductRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorQuoteProductRID] | VendorQuoteProductRID


class VendorQuoteProductAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    tag: Optional[str] = Field(default=None, alias="tag")
    competitor_model: Optional[str] = Field(default=None, alias="competitor-model")
    qty: Optional[int] = Field(default=None, alias="qty")
    price: Optional[int] = Field(default=None, alias="price")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorQuoteProductRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_quotes: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-quotes"
    )
    vendor_products: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-products"
    )
    vendor_quote_products_changelog: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-quote-products-changelog"
    )
    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
    )


class VendorQuoteProductFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_tag: str = Field(default=None, alias="filter[tag]")
    filter_competitor_model: str = Field(default=None, alias="filter[competitor-model]")
    filter_qty: str = Field(default=None, alias="filter[qty]")
    filter_price: str = Field(default=None, alias="filter[price]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorQuoteProductFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_quotes: str = Field(default=None, alias="fields[vendor-quotes]")
    fields_vendor_products: str = Field(default=None, alias="fields[vendor-products]")
    fields_vendor_quote_products_changelog: str = Field(
        default=None, alias="fields[vendor-quote-products-changelog]"
    )
    fields_vendor_quote_products: str = Field(
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
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorQuoteProductQuery: type[BaseModel] = create_model(
    "VendorQuoteProductQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorQuoteProductRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorQuoteProductAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_quote_products": (
            Optional[str],
            None,
        )
    },
)


class VendorQuoteProductQuery(_VendorQuoteProductQuery, BaseModel): ...


class VendorQuoteProductQueryJSONAPI(
    VendorQuoteProductFields, VendorQuoteProductFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorQuoteProductAttrs(BaseModel):
    qty: Optional[int] = Field(default=None, alias="qty")
    price: Optional[int] = Field(default=None, alias="price")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


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
    status: Optional[Stage] = Field(default=None, alias="status")
    timestamp: Optional[datetime] = Field(default=None, alias="timestamp")


class VendorQuoteChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_quotes: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-quotes"
    )


class VendorQuoteChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_status: str = Field(default=None, alias="filter[status]")
    filter_timestamp: str = Field(default=None, alias="filter[timestamp]")


class VendorQuoteChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_quotes: str = Field(default=None, alias="fields[vendor-quotes]")
    fields_vendor_quotes_changelog: str = Field(
        default=None, alias="fields[vendor-quotes-changelog]"
    )


class VendorQuoteChangelogRObj(VendorQuoteChangelogRID):
    attributes: VendorQuoteChangelogAttrs
    relationships: VendorQuoteChangelogRels


class VendorQuoteChangelogResp(JSONAPIResponse):
    data: list[VendorQuoteChangelogRObj] | VendorQuoteChangelogRObj


class RelatedVendorQuoteChangelogResp(VendorQuoteChangelogResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorQuoteChangelogQuery: type[BaseModel] = create_model(
    "VendorQuoteChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorQuoteChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorQuoteChangelogAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_quotes_changelog": (
            Optional[str],
            None,
        )
    },
)


class VendorQuoteChangelogQuery(_VendorQuoteChangelogQuery, BaseModel): ...


class VendorQuoteChangelogQueryJSONAPI(
    VendorQuoteChangelogFields, VendorQuoteChangelogFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorQuoteProductChangelog


class VendorQuoteProductChangelogRID(JSONAPIResourceIdentifier):
    type: str = VendorQuoteProductChangelog.__jsonapi_type_override__


class VendorQuoteProductChangelogRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorQuoteProductChangelogRID] | VendorQuoteProductChangelogRID


class VendorQuoteProductChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    qty: Optional[int] = Field(default=None, alias="qty")
    price: Optional[int] = Field(default=None, alias="price")
    timestamp: Optional[datetime] = Field(default=None, alias="timestamp")


class VendorQuoteProductChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_quote_products: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-quote-products"
    )


class VendorQuoteProductChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_qty: str = Field(default=None, alias="filter[qty]")
    filter_price: str = Field(default=None, alias="filter[price]")
    filter_timestamp: str = Field(default=None, alias="filter[timestamp]")


class VendorQuoteProductChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_quote_products: str = Field(
        default=None, alias="fields[vendor-quote-products]"
    )
    fields_vendor_quote_products_changelog: str = Field(
        default=None, alias="fields[vendor-quote-products-changelog]"
    )


class VendorQuoteProductChangelogRObj(VendorQuoteProductChangelogRID):
    attributes: VendorQuoteProductChangelogAttrs
    relationships: VendorQuoteProductChangelogRels


class VendorQuoteProductChangelogResp(JSONAPIResponse):
    data: list[VendorQuoteProductChangelogRObj] | VendorQuoteProductChangelogRObj


class RelatedVendorQuoteProductChangelogResp(VendorQuoteProductChangelogResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorQuoteProductChangelogQuery: type[BaseModel] = create_model(
    "VendorQuoteProductChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorQuoteProductChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorQuoteProductChangelogAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_quote_products_changelog": (
            Optional[str],
            None,
        )
    },
)


class VendorQuoteProductChangelogQuery(
    _VendorQuoteProductChangelogQuery, BaseModel
): ...


class VendorQuoteProductChangelogQueryJSONAPI(
    VendorQuoteProductChangelogFields, VendorQuoteProductChangelogFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorCustomerPricingClass


class VendorCustomerPricingClassRID(JSONAPIResourceIdentifier):
    type: str = VendorCustomerPricingClass.__jsonapi_type_override__


class VendorCustomerPricingClassRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorCustomerPricingClassRID] | VendorCustomerPricingClassRID


class VendorCustomerPricingClassAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorCustomerPricingClassRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_pricing_classes: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-classes"
    )
    vendor_customers: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customers"
    )


class VendorCustomerPricingClassFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorCustomerPricingClassFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_classes: str = Field(
        default=None, alias="fields[vendor-pricing-classes]"
    )
    fields_vendor_customers: str = Field(default=None, alias="fields[vendor-customers]")
    fields_vendor_customer_pricing_classes: str = Field(
        default=None, alias="fields[vendor-customer-pricing-classes]"
    )


class VendorCustomerPricingClassRObj(VendorCustomerPricingClassRID):
    attributes: VendorCustomerPricingClassAttrs
    relationships: VendorCustomerPricingClassRels


class VendorCustomerPricingClassResp(JSONAPIResponse):
    data: list[VendorCustomerPricingClassRObj] | VendorCustomerPricingClassRObj


class NewVendorCustomerPricingClassRObj(BaseModel):
    type: str = VendorCustomerPricingClass.__jsonapi_type_override__
    attributes: Optional[VendorCustomerPricingClassAttrs] = Field(default=False)
    relationships: VendorCustomerPricingClassRels


class NewVendorCustomerPricingClass(BaseModel):
    data: NewVendorCustomerPricingClassRObj


class RelatedVendorCustomerPricingClassResp(VendorCustomerPricingClassResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorCustomerPricingClassQuery: type[BaseModel] = create_model(
    "VendorCustomerPricingClassQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorCustomerPricingClassRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorCustomerPricingClassAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_customer_pricing_classes": (
            Optional[str],
            None,
        )
    },
)


class VendorCustomerPricingClassQuery(_VendorCustomerPricingClassQuery, BaseModel): ...


class VendorCustomerPricingClassQueryJSONAPI(
    VendorCustomerPricingClassFields, VendorCustomerPricingClassFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


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
    timestamp: Optional[datetime] = Field(default=None, alias="timestamp")


class VendorCustomerPricingClassesChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_pricing_classes: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-classes"
    )
    vendor_customers: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customers"
    )


class VendorCustomerPricingClassesChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_timestamp: str = Field(default=None, alias="filter[timestamp]")


class VendorCustomerPricingClassesChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_classes: str = Field(
        default=None, alias="fields[vendor-pricing-classes]"
    )
    fields_vendor_customers: str = Field(default=None, alias="fields[vendor-customers]")
    fields_vendor_customer_pricing_classes_changelog: str = Field(
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
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorCustomerPricingClassesChangelogQuery: type[BaseModel] = create_model(
    "VendorCustomerPricingClassesChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorCustomerPricingClassesChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorCustomerPricingClassesChangelogAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_customer_pricing_classes_changelog": (
            Optional[str],
            None,
        )
    },
)


class VendorCustomerPricingClassesChangelogQuery(
    _VendorCustomerPricingClassesChangelogQuery, BaseModel
): ...


class VendorCustomerPricingClassesChangelogQueryJSONAPI(
    VendorCustomerPricingClassesChangelogFields,
    VendorCustomerPricingClassesChangelogFilters,
    Query,
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorCustomerChangelog


class VendorCustomerChangelogRID(JSONAPIResourceIdentifier):
    type: str = VendorCustomerChangelog.__jsonapi_type_override__


class VendorCustomerChangelogRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorCustomerChangelogRID] | VendorCustomerChangelogRID


class VendorCustomerChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Optional[str] = Field(default=None, alias="name")
    timestamp: Optional[datetime] = Field(default=None, alias="timestamp")


class VendorCustomerChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_customers: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customers"
    )


class VendorCustomerChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_name: str = Field(default=None, alias="filter[name]")
    filter_timestamp: str = Field(default=None, alias="filter[timestamp]")


class VendorCustomerChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customers: str = Field(default=None, alias="fields[vendor-customers]")
    fields_vendor_customer_changelog: str = Field(
        default=None, alias="fields[vendor-customer-changelog]"
    )


class VendorCustomerChangelogRObj(VendorCustomerChangelogRID):
    attributes: VendorCustomerChangelogAttrs
    relationships: VendorCustomerChangelogRels


class VendorCustomerChangelogResp(JSONAPIResponse):
    data: list[VendorCustomerChangelogRObj] | VendorCustomerChangelogRObj


class RelatedVendorCustomerChangelogResp(VendorCustomerChangelogResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorCustomerChangelogQuery: type[BaseModel] = create_model(
    "VendorCustomerChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorCustomerChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorCustomerChangelogAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_customer_changelog": (
            Optional[str],
            None,
        )
    },
)


class VendorCustomerChangelogQuery(_VendorCustomerChangelogQuery, BaseModel): ...


class VendorCustomerChangelogQueryJSONAPI(
    VendorCustomerChangelogFields, VendorCustomerChangelogFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorCustomerAttr


class VendorCustomerAttrRID(JSONAPIResourceIdentifier):
    type: str = VendorCustomerAttr.__jsonapi_type_override__


class VendorCustomerAttrRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorCustomerAttrRID] | VendorCustomerAttrRID


class VendorCustomerAttrAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    attr: Optional[str] = Field(default=None, alias="attr")
    type: Optional[str] = Field(default=None, alias="type")
    value: Optional[str] = Field(default=None, alias="value")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorCustomerAttrRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_customers: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customers"
    )
    vendor_customer_attrs_changelog: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customer-attrs-changelog"
    )


class VendorCustomerAttrFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_attr: str = Field(default=None, alias="filter[attr]")
    filter_type: str = Field(default=None, alias="filter[type]")
    filter_value: str = Field(default=None, alias="filter[value]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorCustomerAttrFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customers: str = Field(default=None, alias="fields[vendor-customers]")
    fields_vendor_customer_attrs_changelog: str = Field(
        default=None, alias="fields[vendor-customer-attrs-changelog]"
    )
    fields_vendor_customer_attrs: str = Field(
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
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorCustomerAttrQuery: type[BaseModel] = create_model(
    "VendorCustomerAttrQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorCustomerAttrRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorCustomerAttrAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_customer_attrs": (
            Optional[str],
            None,
        )
    },
)


class VendorCustomerAttrQuery(_VendorCustomerAttrQuery, BaseModel): ...


class VendorCustomerAttrQueryJSONAPI(
    VendorCustomerAttrFields, VendorCustomerAttrFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorCustomerAttrAttrs(BaseModel):
    value: Optional[str] = Field(default=None, alias="value")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


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
    attr: Optional[str] = Field(default=None, alias="attr")
    type: Optional[str] = Field(default=None, alias="type")
    value: Optional[str] = Field(default=None, alias="value")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


class VendorQuoteAttrRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_quotes: JSONAPIRelationships = Field(default=None, alias="vendor-quotes")
    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
    )


class VendorQuoteAttrFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_attr: str = Field(default=None, alias="filter[attr]")
    filter_type: str = Field(default=None, alias="filter[type]")
    filter_value: str = Field(default=None, alias="filter[value]")
    filter_deleted_at: str = Field(default=None, alias="filter[deleted-at]")


class VendorQuoteAttrFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_quotes: str = Field(default=None, alias="fields[vendor-quotes]")
    fields_vendor_quotes_attrs: str = Field(
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
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorQuoteAttrQuery: type[BaseModel] = create_model(
    "VendorQuoteAttrQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorQuoteAttrRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorQuoteAttrAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_quotes_attrs": (
            Optional[str],
            None,
        )
    },
)


class VendorQuoteAttrQuery(_VendorQuoteAttrQuery, BaseModel): ...


class VendorQuoteAttrQueryJSONAPI(VendorQuoteAttrFields, VendorQuoteAttrFilters, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


class ModVendorQuoteAttrAttrs(BaseModel):
    value: Optional[str] = Field(default=None, alias="value")
    deleted_at: Optional[datetime] = Field(default=None, alias="deleted-at")


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


class CustomerPricingByClassRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_pricing_by_class: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-by-class"
    )
    users: Optional[JSONAPIRelationships] = Field(default=None, alias="users")


class CustomerPricingByClassFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class CustomerPricingByClassFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_by_class: str = Field(
        default=None, alias="fields[vendor-pricing-by-class]"
    )
    fields_users: str = Field(default=None, alias="fields[users]")
    fields_customer_pricing_by_class: str = Field(
        default=None, alias="fields[customer-pricing-by-class]"
    )


class CustomerPricingByClassRObj(CustomerPricingByClassRID):
    attributes: CustomerPricingByClassAttrs
    relationships: CustomerPricingByClassRels


class CustomerPricingByClassResp(JSONAPIResponse):
    data: list[CustomerPricingByClassRObj] | CustomerPricingByClassRObj


class NewCustomerPricingByClassRObj(BaseModel):
    type: str = CustomerPricingByClass.__jsonapi_type_override__
    attributes: Optional[CustomerPricingByClassAttrs] = Field(default=None)
    relationships: CustomerPricingByClassRels


class NewCustomerPricingByClass(BaseModel):
    data: NewCustomerPricingByClassRObj


class RelatedCustomerPricingByClassResp(CustomerPricingByClassResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_CustomerPricingByClassQuery: type[BaseModel] = create_model(
    "CustomerPricingByClassQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in CustomerPricingByClassRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in CustomerPricingByClassAttrs.model_fields.keys()
    },
    **{
        f"fields_customer_pricing_by_class": (
            Optional[str],
            None,
        )
    },
)


class CustomerPricingByClassQuery(_CustomerPricingByClassQuery, BaseModel): ...


class CustomerPricingByClassQueryJSONAPI(
    CustomerPricingByClassFields, CustomerPricingByClassFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import CustomerPricingByCustomer


class CustomerPricingByCustomerRID(JSONAPIResourceIdentifier):
    type: str = CustomerPricingByCustomer.__jsonapi_type_override__


class CustomerPricingByCustomerRelResp(JSONAPIRelationshipsResponse):
    data: list[CustomerPricingByCustomerRID] | CustomerPricingByCustomerRID


class CustomerPricingByCustomerAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    # gets hard deleted


class CustomerPricingByCustomerRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors", exclude=True
    )
    vendor_pricing_by_customer: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-pricing-by-customer"
    )
    users: Optional[JSONAPIRelationships] = Field(default=None, alias="users")


class CustomerPricingByCustomerFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class CustomerPricingByCustomerFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_pricing_by_customer: str = Field(
        default=None, alias="fields[vendor-pricing-by-customer]"
    )
    fields_users: str = Field(default=None, alias="fields[users]")
    fields_customer_pricing_by_customer: str = Field(
        default=None, alias="fields[customer-pricing-by-customer]"
    )


class CustomerPricingByCustomerRObj(CustomerPricingByCustomerRID):
    attributes: Optional[CustomerPricingByCustomerAttrs] = Field(default=None)
    relationships: CustomerPricingByCustomerRels


class CustomerPricingByCustomerResp(JSONAPIResponse):
    data: list[CustomerPricingByCustomerRObj] | CustomerPricingByCustomerRObj


class RelatedCustomerPricingByCustomerResp(CustomerPricingByCustomerResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


class NewCustomerPricingByCustomerRObj(BaseModel):
    type: str = CustomerPricingByCustomer.__jsonapi_type_override__
    attributes: Optional[CustomerPricingByCustomerAttrs] = Field(default=None)
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
        f"fields_{field}": (Optional[str], None)
        for field in CustomerPricingByCustomerRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in CustomerPricingByCustomerAttrs.model_fields.keys()
    },
    **{
        f"fields_customer_pricing_by_customer": (
            Optional[str],
            None,
        )
    },
)


class CustomerPricingByCustomerQuery(_CustomerPricingByCustomerQuery, BaseModel): ...


class CustomerPricingByCustomerQueryJSONAPI(
    CustomerPricingByCustomerFields, CustomerPricingByCustomerFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorCustomerAttrChangelog


class VendorCustomerAttrChangelogRID(JSONAPIResourceIdentifier):
    type: str = VendorCustomerAttrChangelog.__jsonapi_type_override__


class VendorCustomerAttrChangelogRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorCustomerAttrChangelogRID] | VendorCustomerAttrChangelogRID


class VendorCustomerAttrChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    value: Optional[str] = Field(default=None, alias="value")
    timestamp: Optional[datetime] = Field(default=None, alias="timestamp")


class VendorCustomerAttrChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_customer_attrs: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendor-customer-attrs"
    )


class VendorCustomerAttrChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_value: str = Field(default=None, alias="filter[value]")
    filter_timestamp: str = Field(default=None, alias="filter[timestamp]")


class VendorCustomerAttrChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendor_customer_attrs: str = Field(
        default=None, alias="fields[vendor-customer-attrs]"
    )
    fields_vendor_customer_attrs_changelog: str = Field(
        default=None, alias="fields[vendor-customer-attrs-changelog]"
    )


class VendorCustomerAttrChangelogRObj(VendorCustomerAttrChangelogRID):
    attributes: VendorCustomerAttrChangelogAttrs
    relationships: VendorCustomerAttrChangelogRels


class VendorCustomerAttrChangelogResp(JSONAPIResponse):
    data: list[VendorCustomerAttrChangelogRObj] | VendorCustomerAttrChangelogRObj


class RelatedVendorCustomerAttrChangelogResp(VendorCustomerAttrChangelogResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorCustomerAttrChangelogQuery: type[BaseModel] = create_model(
    "VendorCustomerAttrChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorCustomerAttrChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorCustomerAttrChangelogAttrs.model_fields.keys()
    },
    **{
        f"fields_vendor_customer_attrs_changelog": (
            Optional[str],
            None,
        )
    },
)


class VendorCustomerAttrChangelogQuery(
    _VendorCustomerAttrChangelogQuery, BaseModel
): ...


class VendorCustomerAttrChangelogQueryJSONAPI(
    VendorCustomerAttrChangelogFields, VendorCustomerAttrChangelogFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


from app.jsonapi.sqla_models import VendorsAttrsChangelog


class VendorsAttrsChangelogRID(JSONAPIResourceIdentifier):
    type: str = VendorsAttrsChangelog.__jsonapi_type_override__


class VendorsAttrsChangelogRelResp(JSONAPIRelationshipsResponse):
    data: list[VendorsAttrsChangelogRID] | VendorsAttrsChangelogRID


class VendorsAttrsChangelogAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Optional[str] = Field(default=None, alias="type")
    value: Optional[str] = Field(default=None, alias="value")
    timestamp: Optional[datetime] = Field(default=None, alias="timestamp")


class VendorsAttrsChangelogRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendors_attrs: Optional[JSONAPIRelationships] = Field(
        default=None, alias="vendors-attrs"
    )


class VendorsAttrsChangelogFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_type: str = Field(default=None, alias="filter[type]")
    filter_value: str = Field(default=None, alias="filter[value]")
    filter_timestamp: str = Field(default=None, alias="filter[timestamp]")


class VendorsAttrsChangelogFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_vendors_attrs: str = Field(default=None, alias="fields[vendors-attrs]")
    fields_vendors_attrs_changelog: str = Field(
        default=None, alias="fields[vendors-attrs-changelog]"
    )


class VendorsAttrsChangelogRObj(VendorsAttrsChangelogRID):
    attributes: VendorsAttrsChangelogAttrs
    relationships: VendorsAttrsChangelogRels


class VendorsAttrsChangelogResp(JSONAPIResponse):
    data: list[VendorsAttrsChangelogRObj] | VendorsAttrsChangelogRObj


class RelatedVendorsAttrsChangelogResp(VendorsAttrsChangelogResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


_VendorsAttrsChangelogQuery: type[BaseModel] = create_model(
    "VendorsAttrsChangelogQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in VendorsAttrsChangelogRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None)
        for field in VendorsAttrsChangelogAttrs.model_fields.keys()
    },
    **{
        f"fields_vendors_attrs_changelog": (
            Optional[str],
            None,
        )
    },
)


class VendorsAttrsChangelogQuery(_VendorsAttrsChangelogQuery, BaseModel): ...


class VendorsAttrsChangelogQueryJSONAPI(
    VendorsAttrsChangelogFields, VendorsAttrsChangelogFilters, Query
):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")


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
}
