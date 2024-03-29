
from pydantic import BaseModel, Field, create_model, model_validator, ConfigDict
from typing import Optional
from datetime import datetime
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    JSONAPIVersion,
    Pagination,
    Query
)
from app.db import Stage
from app.jsonapi.sqla_models import (
    ADPAHProgram, ADPCoilProgram,
    ADPCustomerTerms, ADPCustomer,
    ADPProgramRating, ADPProgramPart,
    ADPPricingPart,
)

class CoilProgRID(JSONAPIResourceIdentifier):
    type: str = ADPCoilProgram.__jsonapi_type_override__

class AirHandlerProgRID(JSONAPIResourceIdentifier):
    type: str = ADPAHProgram.__jsonapi_type_override__

class CoilProgRelResp(JSONAPIRelationshipsResponse):
    data: list[CoilProgRID] | CoilProgRID
class AirHandlerProgRelResp(JSONAPIRelationshipsResponse):
    data: list[AirHandlerProgRID] | AirHandlerProgRID

class ProgAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    category: Optional[str] = None
    model_number: Optional[str] = Field(default=None, alias="model-number")
    private_label: Optional[str] = Field(default=None, alias="private-label")
    mpg: Optional[str] = None
    series: Optional[str] = None
    tonnage: Optional[int] = None
    pallet_qty: Optional[int] = Field(default=None, alias='pallet-qty')
    min_qty: Optional[int] = Field(default=None, alias='min-qty')
    width: Optional[float] = None
    depth: Optional[float] = None
    height: Optional[float] = None
    length: Optional[float] = None
    weight: Optional[int] = None
    metering: Optional[str] = None
    cabinet: Optional[str] = None
    motor: Optional[str] = None
    heat: Optional[str] = None
    zero_discount_price: Optional[int] = Field(default=None, alias='zero-discount-price')
    material_group_discount: Optional[float] = Field(default=None, alias='material-group-discount')
    material_group_net_price: Optional[int] = Field(default=None, alias='material-group-net-price')
    snp_discount: Optional[float] = Field(default=None, alias='snp-discount')
    snp_price: Optional[int] = Field(default=None, alias='snp-price')
    net_price: Optional[int] = Field(default=None, alias='net-price')
    effective_date: Optional[datetime] = Field(default=None, alias='effective-date')
    last_file_gen: Optional[datetime] = Field(default=None, alias='last-file-gen')
    stage: Optional[str] = None
    # intentionally leaving out Ratings model regexes
    #   ratings-ac-txv
    #   ratings-hp-txv
    #   ratings-piston
    #   ratings-field-txv
    
    @model_validator(mode='after')
    def depth_or_length(self) -> 'ProgAttrs':
        depth, length = self.depth, self.length
        match depth, length:
            case (float(), float()):
                raise ValueError('Cannot have both depth and length.')
        return self

class ProgFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_category: str = Field(default=None, alias='filter[category]')
    filter_model_number: str = Field(default=None, alias='filter[model-number]')
    filter_private_label: str = Field(default=None, alias='filter[private-label]')
    filter_mpg: str = Field(default=None, alias='filter[mpg]')
    filter_series: str = Field(default=None, alias='filter[series]')
    filter_tonnage: str = Field(default=None, alias='filter[tonnage]')
    filter_pallet_qty: str = Field(default=None, alias='filter[pallet-qty]')
    filter_min_qty: str = Field(default=None, alias='filter[min-qty]')
    filter_width: str = Field(default=None, alias='filter[width]')
    filter_depth: str = Field(default=None, alias='filter[depth]')
    filter_height: str = Field(default=None, alias='filter[height]')
    filter_length: str = Field(default=None, alias='filter[length]')
    filter_weight: str = Field(default=None, alias='filter[weight]')
    filter_metering: str = Field(default=None, alias='filter[metering]')
    filter_cabinet: str = Field(default=None, alias='filter[cabinet]')
    filter_motor: str = Field(default=None, alias='filter[motor]')
    filter_heat: str = Field(default=None, alias='filter[heat]')
    filter_zero_discount_price: str = Field(default=None, alias='filter[zero-discount-price]')
    filter_material_group_discount: str = Field(default=None, alias='filter[material-group-discount]')
    filter_material_group_net_price: str = Field(default=None, alias='filter[material-group-net-price]')
    filter_snp_discount: str = Field(default=None, alias='filter[snp-discount]')
    filter_snp_price: str = Field(default=None, alias='filter[snp-price]')
    filter_net_price: str = Field(default=None, alias='filter[net-price]')
    filter_effective_date: str = Field(default=None, alias='filter[effective-date]')
    filter_last_file_gen: str = Field(default=None, alias='filter[last-file-gen]')
    filter_stage: str = Field(default=None, alias='filter[stage]')


class ProgRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    adp_customers: Optional[JSONAPIRelationships] = Field(default=None, alias='adp-customers')

class ProgFields(BaseModel):
    fields_adp_customers: str = Field(default=None, alias='fields[adp-customer]')

class CoilProgFields(ProgFields):
    fields_adp_coil_programs: str = Field(default=None, alias='fields[adp-coil-programs]')

class AHProgFields(ProgFields):
    fields_adp_ah_programs: str = Field(default=None, alias='fields[adp-ah-programs]')

class CoilProgRObj(CoilProgRID):
    attributes: ProgAttrs
    relationships: ProgRels
class AirHandlerProgRObj(AirHandlerProgRID):
    attributes: ProgAttrs
    relationships: ProgRels

class CoilProgResp(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[CoilProgRObj] | CoilProgRObj]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination] = None

class AirHandlerProgResp(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[AirHandlerProgRObj] | AirHandlerProgRObj]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination] = None

class RelatedCoilProgResp(CoilProgResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)

class RelatedAirHandlerProgResp(AirHandlerProgResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)

_CoilProgQuery: type[BaseModel] = create_model(
    'CoilProgQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f"fields_{field}":(Optional[str], None) for field in ProgRels.model_fields.keys()},
    **{f'fields_{CoilProgRID.model_fields["type"].default.replace("-","_")}': (Optional[str], None)},
    **{f"filter_{field}":(Optional[str], None) for field in ProgAttrs.model_fields.keys()},
)
_AirHandlerProgQuery: type[BaseModel] = create_model(
    'AirHandlerProgQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f"fields_{field}":(Optional[str], None) for field in ProgRels.model_fields.keys()},
    **{f'fields_{AirHandlerProgRID.model_fields["type"].default.replace("-","_")}': (Optional[str], None)},
    **{f"filter_{field}":(Optional[str], None) for field in ProgAttrs.model_fields.keys()},
)
class AirHandlerProgQuery(_AirHandlerProgQuery, BaseModel): ...
class CoilProgQuery(_CoilProgQuery, BaseModel): ...

class CoilProgQueryJSONAPI(CoilProgFields, ProgFilters, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")

class AHProgQueryJSONAPI(AHProgFields, ProgFilters, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")

## New Models to a Program
class NewModelNumber(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    model_number: str = Field(alias="model-number")

class NewPartNumber(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    part_number: str = Field(alias="part-number")
class NewCoilRObj(BaseModel):
    type: str = ADPCoilProgram.__jsonapi_type_override__
    attributes: NewModelNumber

class NewAHRObj(BaseModel):
    type: str = ADPAHProgram.__jsonapi_type_override__
    attributes: NewModelNumber

class NewPartRObj(BaseModel):
    type: str = ADPProgramPart.__jsonapi_type_override__
    attributes: NewPartNumber

## Modifications to products in a Program
class NewStage(BaseModel):
    stage: Stage

class ModStageCoil(BaseModel):
    id: int
    type: str = ADPCoilProgram.__jsonapi_type_override__
    attributes: NewStage

class ModStageAH(BaseModel):
    id: int
    type: str = ADPAHProgram.__jsonapi_type_override__
    attributes: NewStage

class ModStageAHReq(BaseModel):
    data: ModStageAH

class ModStageCoilReq(BaseModel):
    data: ModStageCoil

## Ratings
class Rating(BaseModel):
    AHRINumber: Optional[int] = None
    OutdoorModel: Optional[str] = None
    OEMName: Optional[str] = None
    IndoorModel: Optional[str] = None
    FurnaceModel: Optional[str] = None
    SEER2: Optional[float] = None
    EER95F2: Optional[float] = None
    Capacity2: Optional[int] = None
    HSPF2: Optional[float] = None

class RatingExpanded(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    AHRINumber: Optional[str] = Field(default=None, alias='ahrinumber')
    OutdoorModel: Optional[str] = Field(default=None, alias='outdoor-model')
    IndoorModel: Optional[str] = Field(default=None, alias='indoor-model')
    FurnaceModel: Optional[str] = Field(default=None, alias='furnace-model')
    OEMName: Optional[str] = Field(default=None, alias='oem-name')
    oem_name_2: Optional[str] = Field(default=None, alias='oem-name-1')
    m1: Optional[str] = None
    status: Optional[str] = None
    oem_series: Optional[str] = Field(default=None, alias='OEM Series')
    adp_series: Optional[str] = Field(default=None, alias='ADP Series')
    model_number: Optional[str] = Field(default=None, alias='Model Number')
    coil_model_number: Optional[str] = Field(default=None, alias='Coil Model Number')
    furnace_model_number: Optional[str] = Field(default=None, alias='Furnace Model Number')
    seer: Optional[float] = None
    eer: Optional[float] = None
    capacity: Optional[float] = None
    four_seven_o: Optional[float] = Field(default=None, alias='-47o', serialization_alias='47o')
    one_seven_o: Optional[float] = Field(default=None, alias='-17o', serialization_alias='17o')
    hspf: Optional[float] = None
    seer2: Optional[float] = None
    eer2: Optional[float] = None
    capacity2: Optional[float] = None
    four_seven_o2: Optional[float] = Field(default=None, alias='-47o2', serialization_alias='47o2')
    one_seven_o2: Optional[float] = Field(default=None, alias='-17o2', serialization_alias='17o2')
    hspf2: Optional[float] = None
    ahri_ref_number: Optional[int] = Field(default=None, alias='AHRI Ref Number')
    region: Optional[str] = None
    effective_date: str = Field(alias='effective-date')
    seer2_as_submitted: Optional[float] = Field(alias='seer2-as-submitted')
    eer95f2_as_submitted: Optional[float] = Field(alias='eer95f2-as-submitted')
    capacity2_as_submitted: Optional[float] = Field(alias='capacity2-as-submitted')
    hspf2_as_submitted: Optional[float] = Field(alias='hspf2-as-submitted')


class Ratings(BaseModel):
    model_config = ConfigDict(extra='ignore')
    ratings: list[Rating]

class RatingsExpanded(BaseModel):
    ratings: list[RatingExpanded]

class RatingsRID(JSONAPIResourceIdentifier):
    type: str = ADPProgramRating.__jsonapi_type_override__

class RatingsRelResp(JSONAPIRelationshipsResponse):
    data: list[RatingsRID] | RatingsRID

class RatingsRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    adp_customers: Optional[JSONAPIRelationships] = Field(default=None, alias='adp-customers')

class RatingsRObj(RatingsRID):
    attributes: Rating
    relationships: RatingsRels

class RatingsExpandedRObj(RatingsRID):
    attributes: RatingExpanded
    relationships: RatingsRels

class RatingsResp(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[RatingsRObj] | RatingsRObj]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination] = {}

class RelatedRatingsResponse(RatingsResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)
    data: Optional[list[RatingsExpandedRObj] | RatingsExpandedRObj]

_RatingsQuery: type[BaseModel] = create_model(
    'RatingsQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f'fields_{RatingsRID.model_fields["type"].default.replace("-","_")}': (Optional[str], None)},
    **{f"fields_{field}":(Optional[str], None) for field in RatingsRels.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in Rating.model_fields.keys()},
)

class RatingsQuery(_RatingsQuery, BaseModel): ...

## Parts
class Parts(BaseModel):
    ...
class PartsRID(JSONAPIResourceIdentifier):
    type: str = ADPProgramPart.__jsonapi_type_override__

class PartsRelResp(JSONAPIRelationshipsResponse):
    data: list[PartsRID] | PartsRID

class PartsRels(BaseModel):
    adp_pricing_parts: Optional[JSONAPIRelationships] = Field(default=None, alias=ADPPricingPart.__jsonapi_type_override__)
    adp_customers: Optional[JSONAPIRelationships] = Field(default=None, alias=ADPCustomer.__jsonapi_type_override__)

class PartsFields(BaseModel):
    fields_adp_pricing_parts: str = Field(default=None, alias=f'fields[{ADPPricingPart.__jsonapi_type_override__}]')
    fields_adp_customers: str = Field(default=None, alias=f'fields[{ADPCustomer.__jsonapi_type_override__}]')

class PartsRObj(PartsRID):
    attributes: Parts
    relationships: PartsRels

class PartsResp(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[PartsRObj] | PartsRObj]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination] = {}

_PartsQuery: type[BaseModel] = create_model(
    'PartsQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f'fields_{PartsRID.model_fields["type"].default.replace("-","_")}': (Optional[str], None)},
    **{f"fields_{field}":(Optional[str], None) for field in PartsRels.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in Parts.model_fields.keys()},
)
class PartsQuery(_PartsQuery, BaseModel): ...

class PartsQueryJSONAPI(PartsFields, Query):
    page_number: str = Field(default=None, alias='page[number]')
    page_size: str = Field(default=None, alias='page[size]')

class RelatedPartsResponse(PartsResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)

    
## Downloads
class DownloadLink(BaseModel):
    downloadLink: str

## ADP Customers
class CustomersRID(JSONAPIResourceIdentifier):
    type: str = ADPCustomer.__jsonapi_type_override__

class CustomersRelResp(JSONAPIRelationshipsResponse):
    data: list[CustomersRID] | CustomersRID

class CustomersAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    adp_alias: Optional[str] = Field(default=None, alias='adp-alias')
    preferred_parts: Optional[bool] = Field(default=None, alias='preferred-parts')

class CustomerFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    filter_adp_alias: str = Field(default=None, alias='filter[adp-alias]')
    filter_preferred_parts: bool = Field(default=None, alias='filter[preferred-parts]')

class CustomersRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    customers: Optional[JSONAPIRelationships] = Field(default=None, alias='customers')
    adp_coil_programs: Optional[JSONAPIRelationships] = Field(default=None, alias='adp-coil-programs')
    adp_ah_programs: Optional[JSONAPIRelationships] = Field(default=None, alias='adp-ah-programs')
    adp_program_ratings: Optional[JSONAPIRelationships] = Field(default=None, alias='adp-program-ratings')
    adp_alias_to_sca_customer_locations: Optional[JSONAPIRelationships] = Field(default=None, alias='adp-alias-to-sca-customer-locations')
    adp_material_group_discounts: Optional[JSONAPIRelationships] = Field(default=None, alias='adp-material-group-discounts')
    adp_snps: Optional[JSONAPIRelationships] = Field(default=None, alias='adp-snps')
    adp_program_parts: Optional[JSONAPIRelationships] = Field(default=None, alias='adp-program-parts')
    adp_quotes: Optional[JSONAPIRelationships] = Field(default=None, alias='adp-quotes')

class CustomerFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    fields_adp_customers: str = Field(default=None, alias='fields[adp-customers]')
    fields_customers: str = Field(default=None, alias='fields[customers]')
    fields_adp_coil_programs: str = Field(default=None, alias='fields[adp-coil-programs]')
    fields_adp_ah_programs: str = Field(default=None, alias='fields[adp-ah-programs]')
    fields_adp_program_ratings: str = Field(default=None, alias='fields[adp-program-ratings]')
    fields_adp_alias_to_sca_customer_locations: str = Field(default=None, alias='fields[adp-alias-to-sca-customer-locations]')
    fields_adp_material_group_discounts: str = Field(default=None, alias='fields[adp-material-group-discounts]')
    fields_adp_snps: str = Field(default=None, alias='fields[adp-snps]')
    fields_adp_program_parts: str = Field(default=None, alias='fields[adp-program-parts]')
    fields_adp_quotes: str = Field(default=None, alias='fields[adp-quotes]')

class CustomersRObj(CustomersRID):
    attributes: Optional[CustomersAttrs] = {}
    relationships: Optional[CustomersRels] = {}

class CustomersResp(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[CustomersRObj] | CustomersRObj]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination] = {}

class RelatedCustomerResponse(CustomersResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)

_CustomersQuery: type[BaseModel] = create_model(
    'CustomersQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f'fields_{CustomersRID.model_fields["type"].default.replace("-","_")}': (Optional[str], None)},
    **{f"fields_{field}":(Optional[str], None) for field in CustomersRels.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in CustomersAttrs.model_fields.keys()},
)
class CustomersQuery(_CustomersQuery, BaseModel): ...

class CustomersQueryJSONAPI(CustomerFields, CustomerFilters, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")

## ADP Customer Terms
class ADPCustomerTermsRID(JSONAPIResourceIdentifier):
    type: str = ADPCustomerTerms.__jsonapi_type_override__

class ADPCustomerTermsRelationshipsResp(JSONAPIRelationshipsResponse):
    data: list[ADPCustomerTermsRID] | ADPCustomerTermsRID

class ADPCustomerTerms(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    terms: str
    ppf: int
    effective_date: datetime = Field(alias='effective-date')

class ADPCustomerTermsRels(BaseModel):
    customers: JSONAPIRelationships

class ADPCustomerTermsRObj(ADPCustomerTermsRID):
    attributes: ADPCustomerTerms
    relationships: ADPCustomerTermsRels

class ADPCustomerTermsResp(BaseModel):
    jsonapi: Optional[JSONAPIVersion] = None
    meta: Optional[dict] = {}
    data: Optional[list[ADPCustomerTermsRObj] | ADPCustomerTermsRObj]
    included: Optional[list[JSONAPIResourceObject]] = None
    links: Optional[Pagination] = None

class RelatedADPCustomerTermsResp(ADPCustomerTermsResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)
