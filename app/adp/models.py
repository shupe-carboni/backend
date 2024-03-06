
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

class CoilProgRID(JSONAPIResourceIdentifier):
    type: str = "adp-coil-programs"

class CoilProgRelResp(JSONAPIRelationshipsResponse):
    data: list[CoilProgRID] | CoilProgRID

class CoilProgAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    category: str
    model_number: str = Field(alias="model-number")
    private_label: str = Field(alias="private-label")
    mpg: str
    series: str
    tonnage: int
    pallent_qty: int = Field(alias='pallet-qty')
    width: float
    depth: float | None
    height: float
    length: float | None
    weight: int | None
    metering: str
    cabinet: str
    zero_discount_price: int = Field(alias='zero-discount-price')
    matieral_group_discount: int = Field(alias='matieral-group-discount')
    material_group_net_price: int = Field(alias='material-group-net-price')
    snp_discount: int = Field(alias='snp-discount')
    snp_price: int = Field(alias='snp-price')
    net_price: int = Field(alias='net-price')
    effective_date: datetime = Field(alias='effective-date')
    last_file_gen: datetime = Field(alias='last-file-gen')
    stage: str
    # intentionally leaving out Ratings model regexes
    #   ratings-ac-txv
    #   ratings-hp-txv
    #   ratings-piston
    #   ratings-field-txv
    
    @model_validator(mode='after')
    def depth_or_length(self) -> 'CoilProgAttrs':
        depth, length = self.depth, self.length
        match depth, length:
            case (None, None):
                raise ValueError('Either depth or length is required')
            case (float(), float()):
                raise ValueError('Cannot have both depth and length.')
        return self


class CoilProgRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    adp_alias: JSONAPIRelationships = Field(alias='adp-alias')

class CoilProgRObj(CoilProgRID):
    attributes: CoilProgAttrs
    relationships: CoilProgRels

class CoilProgResp(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[CoilProgRObj]]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination]

CoilProgQuery: type[BaseModel] = create_model(
    'CoilProgQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f"fields_{field}":(Optional[str], None) for field in CoilProgRels.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in CoilProgAttrs.model_fields.keys()},
)


## New Models to a Program
class NewModelNumber(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    model_number: str = Field(alias="model-number")
class NewCoilRObj(BaseModel):
    type: str = 'adp-coil-programs'
    attributes: NewModelNumber

class NewAHRObj(BaseModel):
    type: str = 'adp-ah-programs'
    attributes: NewModelNumber


## Ratings
class Rating(BaseModel):
    AHRINumber: Optional[int] = None
    OutdoorModel: str
    OEMName: str
    IndoorModel: str
    FurnaceModel: Optional[str] = None
    SEER2: float
    EER95F2: float
    Capacity2: int
    HSPF2: Optional[float] = None
class Ratings(BaseModel):
    model_config = ConfigDict(extra='ignore')
    ratings: list[Rating]

class RatingsRID(JSONAPIResourceIdentifier):
    type: str = "adp-program-ratings"

class RatingsRelResp(JSONAPIRelationshipsResponse):
    data: list[RatingsRID] | RatingsRID

class RatingsRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    adp_customer: JSONAPIRelationships = Field(alias='adp-customer')

class RatingsRObj(RatingsRID):
    attributes: Rating
    relationships: RatingsRels

class RatingsResp(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[list[RatingsRObj]]
    included: Optional[list[JSONAPIResourceObject]]
    links: Optional[Pagination]

RatingsQuery: type[BaseModel] = create_model(
    'RatingsQuery',
    **{field: (field_info.annotation, field_info) for field, field_info in Query.model_fields.items()},
    **{f"fields_{field}":(Optional[str], None) for field in RatingsRels.model_fields.keys()},
    **{f"filter_{field}":(Optional[str], None) for field in Rating.model_fields.keys()},
)

## Parts
class Parts(BaseModel):
    parts: list[str]
    
## Downloads
class DownloadLink(BaseModel):
    downloadLink: str

## ADP Customers
class CustomersRID(JSONAPIResourceIdentifier):
    type: str = "adp-customers"

class CustomersRelResp(JSONAPIRelationshipsResponse):
    data: list[CustomersRID] | CustomersRID

class CustomersAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    adp_alias: str = Field(alias='adp-alias')
    preferred_parts: bool = Field(alias='preferred-parts')
class CustomersRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    customer: JSONAPIRelationships = Field(alias='customer')
    adp_coil_program: JSONAPIRelationships = Field(alias='adp-coil-program')
    adp_ah_program: JSONAPIRelationships = Field(alias='adp-ah-program')
    adp_ratings: JSONAPIRelationships = Field(alias='adp-ratings')
    locations_by_alias: JSONAPIRelationships = Field(alias='locations-by-alias')
    material_group_discounts: JSONAPIRelationships = Field(alias='material-group-discounts')
    snps: JSONAPIRelationships = Field(alias='snps')
    program_parts: JSONAPIRelationships = Field(alias='program-parts')
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