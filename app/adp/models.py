
from pydantic import BaseModel, Field, create_model, root_validator
from typing import Optional
from app.jsonapi import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResourceObject,
    Pagination,
    Query
)

class CoilProgRID(JSONAPIResourceIdentifier):
    type: str = "adp-coil-programs"

class CoilProgRelResp(JSONAPIRelationshipsResponse):
    data: list[CoilProgRID] | CoilProgRID

class CoilProgAttrs(BaseModel):
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
    # intentionally leaving out Ratings model regexes
    #   ratings-ac-txv
    #   ratings-hp-txv
    #   ratings-piston
    #   ratings-field-txv
    effective_date: int = Field(alias='effective-date')
    last_file_gen: int = Field(alias='last-file-gen')
    stage: int

    class Config:
        # allows an unpack of the python-dict in snake_case
        populate_by_name = True
    
    @root_validator(pre=False, skip_on_failure=True)
    def depth_or_length(cls, values: dict):
        depth = values.get('depth')
        length = values.get('length')
        depth_length = (depth, length)
        match depth_length:
            case (None, None):
                raise ValueError('Either depth or length should be specified')
            case (float(), float()):
                raise ValueError('Cannot have both depth and length specified. One or the other should be left blank.')
            case _:
                return values


class CoilProgRels(BaseModel):
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