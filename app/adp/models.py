from pydantic import BaseModel, Field, create_model, model_validator, ConfigDict
from typing import Optional
from datetime import datetime
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIVersion,
    JSONAPIResponse,
    Query,
)
from app.jsonapi.sqla_models import ADPProgramRating


class ProgAttrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True, protected_namespaces={})
    effective_date: Optional[datetime] = Field(default=None, alias="effective-date")
    category: Optional[str] = None
    description: Optional[str] = None
    model_number: Optional[str] = Field(default=None, alias="model-number")
    private_label: Optional[str] = Field(default=None, alias="private-label")
    top_level_class: Optional[str] = None
    mpg: Optional[str] = None
    series: Optional[str] = None
    tonnage: Optional[int] = None
    pallet_qty: Optional[int] = Field(default=None, alias="pallet-qty")
    min_qty: Optional[int] = Field(default=None, alias="min-qty")
    width: Optional[float] = None
    depth: Optional[float] = None
    height: Optional[float] = None
    length: Optional[float] = None
    weight: Optional[int] = None
    metering: Optional[str] = None
    cabinet: Optional[str] = None
    motor: Optional[str] = None
    heat: Optional[str] = None
    cfm: Optional[str] = None
    zero_discount_price: Optional[int] = Field(
        default=None, alias="zero-discount-price"
    )
    standard_price: Optional[int] = Field(default=None, alias="standard-price")
    preferred_price: Optional[int] = Field(default=None, alias="preferred-price")
    material_group_discount: Optional[float] = Field(
        default=None, alias="material-group-discount"
    )
    material_group_net_price: Optional[int] = Field(
        default=None, alias="material-group-net-price"
    )
    snp_discount: Optional[float] = Field(default=None, alias="snp-discount")
    snp_price: Optional[int] = Field(default=None, alias="snp-price")
    net_price: Optional[int] = Field(default=None, alias="net-price")
    effective_date: Optional[datetime] = Field(default=None, alias="effective-date")
    last_file_gen: Optional[datetime] = Field(default=None, alias="last-file-gen")
    stage: Optional[str] = None
    ratings_ac_txv: Optional[str] = Field(default=None, alias="ratings-ac-txv")
    ratings_hp_txv: Optional[str] = Field(default=None, alias="ratings-hp-txv")
    ratings_piston: Optional[str] = Field(default=None, alias="ratings-piston")
    ratings_field_txv: Optional[str] = Field(default=None, alias="ratings-field-txv")

    @model_validator(mode="after")
    def depth_or_length(self) -> "ProgAttrs":
        depth, length = self.depth, self.length
        match depth, length:
            case (float(), float()):
                raise ValueError("Cannot have both depth and length.")
        return self


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
    model_config = ConfigDict(populate_by_name=True, protected_namespaces={})
    AHRINumber: Optional[str] = Field(default=None, alias="ahrinumber")
    OutdoorModel: Optional[str] = Field(default=None, alias="outdoor-model")
    IndoorModel: Optional[str] = Field(default=None, alias="indoor-model")
    FurnaceModel: Optional[str] = Field(default=None, alias="furnace-model")
    OEMName: Optional[str] = Field(default=None, alias="oem-name")
    oem_name_2: Optional[str] = Field(default=None, alias="oem-name-1")
    m1: Optional[str] = None
    status: Optional[str] = None
    oem_series: Optional[str] = Field(default=None, alias="OEM Series")
    adp_series: Optional[str] = Field(default=None, alias="ADP Series")
    model_number: Optional[str] = Field(default=None, alias="Model Number")
    coil_model_number: Optional[str] = Field(default=None, alias="Coil Model Number")
    furnace_model_number: Optional[str] = Field(
        default=None, alias="Furnace Model Number"
    )
    seer: Optional[float] = None
    eer: Optional[float] = None
    capacity: Optional[float] = None
    four_seven_o: Optional[float] = Field(
        default=None, alias="-47o", serialization_alias="47o"
    )
    one_seven_o: Optional[float] = Field(
        default=None, alias="-17o", serialization_alias="17o"
    )
    hspf: Optional[float] = None
    seer2: Optional[float] = None
    eer2: Optional[float] = None
    capacity2: Optional[float] = None
    four_seven_o2: Optional[float] = Field(
        default=None, alias="-47o2", serialization_alias="47o2"
    )
    one_seven_o2: Optional[float] = Field(
        default=None, alias="-17o2", serialization_alias="17o2"
    )
    hspf2: Optional[float] = None
    ahri_ref_number: Optional[int] = Field(default=None, alias="AHRI Ref Number")
    region: Optional[str] = None
    effective_date: str = Field(alias="effective-date")
    seer2_as_submitted: Optional[float] = Field(alias="seer2-as-submitted")
    eer95f2_as_submitted: Optional[float] = Field(alias="eer95f2-as-submitted")
    capacity2_as_submitted: Optional[float] = Field(alias="capacity2-as-submitted")
    hspf2_as_submitted: Optional[float] = Field(alias="hspf2-as-submitted")


class Ratings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ratings: list[Rating]


class RatingsExpanded(BaseModel):
    ratings: list[RatingExpanded]


class RatingsRID(JSONAPIResourceIdentifier):
    type: str = ADPProgramRating.__jsonapi_type_override__


class RatingsRelResp(JSONAPIRelationshipsResponse):
    data: list[RatingsRID] | RatingsRID


class RatingsRels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    adp_customers: Optional[JSONAPIRelationships] = Field(
        default=None, alias="adp-customers"
    )


class RatingsRObj(RatingsRID):
    attributes: Rating
    relationships: RatingsRels


class RatingsExpandedRObj(RatingsRID):
    attributes: RatingExpanded
    relationships: RatingsRels


class RatingsResp(JSONAPIResponse):
    data: Optional[list[RatingsRObj] | RatingsRObj]


class RelatedRatingsResponse(RatingsResp):
    jsonapi: Optional[JSONAPIVersion] = None
    included: dict = {}
    links: Optional[dict] = Field(default=None, exclude=True)
    data: Optional[list[RatingsExpandedRObj] | RatingsExpandedRObj]


_RatingsQuery: type[BaseModel] = create_model(
    "RatingsQuery",
    **{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    },
    **{
        f'fields_{RatingsRID.model_fields["type"].default.replace("-","_")}': (
            Optional[str],
            None,
        )
    },
    **{
        f"fields_{field}": (Optional[str], None)
        for field in RatingsRels.model_fields.keys()
    },
    **{
        f"filter_{field}": (Optional[str], None) for field in Rating.model_fields.keys()
    },
)


class RatingsQuery(_RatingsQuery, BaseModel): ...
