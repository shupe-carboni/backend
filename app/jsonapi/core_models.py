"""
Define the JSON:API specification, which acts as a contract
for requests and responses for the API
"""

from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Annotated, Any, Callable

StringToNum = Annotated[int, BeforeValidator(lambda num: int(num))]


class JSONAPIVersion(BaseModel):
    version: str


class JSONAPIResourceObject(BaseModel):
    id: str | int
    type: str
    attributes: Optional[dict] = {}
    relationships: Optional[dict] = {}


class JSONAPIErrorObject(BaseModel):
    id: str
    meta: Optional[dict] = {}
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
    next: Optional[str] = None
    last: str


class JSONAPIResponse(BaseModel):
    jsonapi: Optional[JSONAPIVersion] = None
    meta: Optional[dict] = {}
    data: Optional[JSONAPIResourceObject]
    included: Optional[list[JSONAPIResourceObject]] = []
    links: Optional[Pagination] = None


class JSONAPIResourceIdentifier(BaseModel):
    id: int | str
    type: str


class JSONAPIRelationshipsResponse(BaseModel):
    meta: Optional[dict] = {}
    data: list[JSONAPIResourceIdentifier] | JSONAPIResourceIdentifier


class JSONAPIRelationshipLinks(BaseModel):
    self: str
    related: str


class JSONAPIRelationships(BaseModel):
    links: Optional[JSONAPIRelationshipLinks] = None
    data: Optional[JSONAPIResourceIdentifier | list[JSONAPIResourceIdentifier]] = None


class JSONAPIRequestData(BaseModel):
    data: JSONAPIResourceObject


class JSONAPIRequest(BaseModel):
    data: JSONAPIRequestData
    included: Optional[list[JSONAPIResourceObject]] = None


class Query(BaseModel):
    include: Optional[str | None] = None
    sort: Optional[str] = None
    # fields: implemented at runtime
    # filter: implemented at runtime
    page_number: Optional[StringToNum] = None
    page_size: Optional[StringToNum] = None


def convert_query(model_type: BaseModel) -> Callable[[BaseModel], dict[str, Any]]:
    """Use the model_type as a converter to transform a query from it's pydantic type
    into a dict of JSONAPI arguments"""

    def inner(query_model: BaseModel) -> dict[str, Any]:
        return model_type(**query_model.model_dump(exclude_none=True)).model_dump(
            by_alias=True, exclude_none=True
        )

    return inner
