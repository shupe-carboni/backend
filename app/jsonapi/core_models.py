"""
Define the JSON:API specification, which acts as a contract
for requests and responses for the API
"""

from pydantic import BaseModel, BeforeValidator, WrapValidator, ValidationError, Field
from typing import Optional, Annotated, Any, Callable
from functools import partial
from datetime import datetime
from app.db import Stage


def set_default(type_: type, v, handler):
    try:
        return handler(v)
    except ValidationError:
        return type_() if type_ is not None else None


set_none_default = partial(set_default, None)
set_list_default = partial(set_default, list)
set_dict_default = partial(set_default, dict)

# Long = Field(ge=-(2**63), le=2**63 - 1)
Long = Field(ge=1000000000, le=9999999999)

StringToNum = Annotated[int, BeforeValidator(lambda num: int(num))]

NullableStr = Annotated[str, WrapValidator(set_none_default)]
NullableInt = Annotated[int, WrapValidator(set_none_default)]
NullableLongInt = Annotated[int, Long, WrapValidator(set_none_default)]
NullableFloat = Annotated[float, WrapValidator(set_none_default)]
NullableBool = Annotated[bool, WrapValidator(set_none_default)]
NullableDateTime = Annotated[datetime, WrapValidator(set_none_default)]
NullableStage = Annotated[Stage, WrapValidator(set_none_default)]

OptionalDict = Annotated[dict, WrapValidator(set_dict_default)]
OptionalList = Annotated[list, WrapValidator(set_list_default)]
OptionalIntArr = Annotated[list[int], WrapValidator(set_list_default)]


class JSONAPIVersion(BaseModel):
    version: str


OptionalJSONAPIVersion = Annotated[JSONAPIVersion, WrapValidator(set_none_default)]


class JSONAPIResourceObject(BaseModel):
    id: int
    type: str
    attributes: OptionalDict
    relationships: OptionalDict


OptionalJSONAPIResourceObject = Annotated[
    JSONAPIResourceObject, WrapValidator(set_none_default)
]
OptionalArrJSONAPIResourceObject = Annotated[
    list[JSONAPIResourceObject], WrapValidator(set_none_default)
]


class JSONAPIErrorObject(BaseModel):
    id: str
    meta: OptionalDict
    status: int
    code: str
    title: str
    detail: str


class JSONAPIErrorResponse(BaseModel):
    errors: list[JSONAPIErrorObject]


class Pagination(BaseModel):
    # self: str
    first: str
    # prev: str
    next: NullableStr
    last: str


OptionalPagination = Annotated[Pagination, WrapValidator(set_none_default)]


class JSONAPIResponse(BaseModel):
    jsonapi: OptionalJSONAPIVersion
    meta: OptionalDict
    data: OptionalJSONAPIResourceObject
    included: OptionalArrJSONAPIResourceObject
    links: OptionalPagination = None


class JSONAPIResourceIdentifier(BaseModel):
    id: int | str
    type: str


OptionalJSONAPIResourceIdentifier = Annotated[
    JSONAPIResourceIdentifier, WrapValidator(set_none_default)
]
OptionalArrJSONAPIResourceIdentifier = Annotated[
    list[JSONAPIResourceIdentifier], WrapValidator(set_none_default)
]


class JSONAPIRelationshipsResponse(BaseModel):
    meta: OptionalDict
    data: list[JSONAPIResourceIdentifier]


class JSONAPIRelationshipLinks(BaseModel):
    self: str
    related: str


OptionalJSONAPIRelationshipLinks = Annotated[
    JSONAPIRelationshipLinks, WrapValidator(set_none_default)
]


class JSONAPIRelationships(BaseModel):
    links: OptionalJSONAPIRelationshipLinks = None
    data: OptionalArrJSONAPIResourceIdentifier = None


OptionalJSONAPIRelationships = Annotated[
    JSONAPIRelationships, WrapValidator(set_none_default)
]


class JSONAPIRequestData(BaseModel):
    data: JSONAPIResourceObject


class JSONAPIRequest(BaseModel):
    data: JSONAPIRequestData
    included: OptionalArrJSONAPIResourceObject


class Query(BaseModel):
    include: NullableStr = None
    sort: NullableStr = None
    # fields: implemented at runtime
    # filter: implemented at runtime
    page_number: Optional[StringToNum] = None
    page_size: Optional[StringToNum] = None


def convert_query(model_type: type[BaseModel]) -> Callable[[BaseModel], dict[str, Any]]:
    """Use the model_type as a converter to transform a query from it's pydantic type
    into a dict of JSONAPI arguments"""

    def inner(query_model: BaseModel) -> dict[str, Any]:
        return model_type(**query_model.model_dump(exclude_none=True)).model_dump(
            by_alias=True, exclude_none=True
        )

    return inner
