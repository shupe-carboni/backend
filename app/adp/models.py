
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
    width: Optional[float] = None
    depth: Optional[float] = None
    height: Optional[float] = None
    length: Optional[float] = None
    weight: Optional[int] = None
    metering: Optional[str] = None
    cabinet: Optional[str] = None
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


class ProgRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    adp_customers: Optional[JSONAPIRelationships] = Field(default=None, alias='adp-customers')

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
class AirHandlerProgQuery(_AirHandlerProgQuery): ...
class CoilProgQuery(_CoilProgQuery): ...

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

class Ratings(BaseModel):
    model_config = ConfigDict(extra='ignore')
    ratings: list[Rating]

class RatingsRID(JSONAPIResourceIdentifier):
    type: str = ADPProgramRating.__jsonapi_type_override__

class RatingsRelResp(JSONAPIRelationshipsResponse):
    data: list[RatingsRID] | RatingsRID

class RatingsRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    adp_customer: Optional[JSONAPIRelationships] = Field(default=None, alias='adp-customer')

class RatingsRObj(RatingsRID):
    attributes: Rating
    relationships: RatingsRels

class RatingsResp(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[RatingsRObj] | RatingsRObj]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination]

_RatingsQuery: type[BaseModel] = create_model(
    'RatingsQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f'fields_{RatingsRID.model_fields["type"].default.replace("-","_")}': (Optional[str], None)},
    **{f"fields_{field}":(Optional[str], None) for field in RatingsRels.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in Rating.model_fields.keys()},
)

class RatingsQuery(_RatingsQuery): ...

## Parts
class Parts(BaseModel):
    ...
class PartsRID(JSONAPIResourceIdentifier):
    type: str = ADPProgramPart.__jsonapi_type_override__

class PartsRelResp(JSONAPIRelationshipsResponse):
    data: list[PartsRID] | PartsRID

class PartsRels(BaseModel):
    adp_pricing_parts: Optional[JSONAPIRelationships] = Field(default=None, alias=ADPPricingPart.__jsonapi_type_override__)
    adp_customers: Optional[JSONAPIRelationships] = Field(default=None, alias=ADPProgramPart.__jsonapi_type_override__)

class PartsRObj(PartsRID):
    attributes: Parts
    relationships: PartsRels

class PartsResp(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[PartsRObj] | PartsRObj]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination]

_PartsQuery: type[BaseModel] = create_model(
    'PartsQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f'fields_{PartsRID.model_fields["type"].default.replace("-","_")}': (Optional[str], None)},
    **{f"fields_{field}":(Optional[str], None) for field in PartsRels.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in Rating.model_fields.keys()},
)
class PartsQuery(_PartsQuery): ...
    
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
    adp_alias: str = Field(alias='adp-alias')
    preferred_parts: bool = Field(alias='preferred-parts')
class CustomersRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    customers: JSONAPIRelationships = Field(alias='customers')
    adp_coil_programs: JSONAPIRelationships = Field(alias='adp-coil-programs')
    adp_ah_programs: JSONAPIRelationships = Field(alias='adp-ah-programs')
    adp_program_ratings: JSONAPIRelationships = Field(alias='adp-program-ratings')
    adp_alias_to_sca_customer_locations: JSONAPIRelationships = Field(alias='adp-alias-to-sca-customer-locations')
    adp_material_group_discounts: JSONAPIRelationships = Field(alias='adp-material-group-discounts')
    adp_snps: JSONAPIRelationships = Field(alias='adp-snps')
    adp_program_parts: JSONAPIRelationships = Field(alias='adp-program-parts')
    adp_quotes: JSONAPIRelationships = Field(alias='adp-quotes')
class CustomersRObj(CustomersRID):
    attributes: CustomersAttrs
    relationships: CustomersRels

class CustomersResp(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[CustomersRObj]]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination]

class RelatedCustomerResponse(CustomersResp):
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)


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
