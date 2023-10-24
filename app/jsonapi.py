"""
Define the JSON:API specification, which acts as a contract
for requests and responses for the API
"""

from pydantic import BaseModel
from typing import Optional

JSONAPI_CONTENT_TYPE = 'application/vnd.api+json'

class JSONAPIResourceObject(BaseModel):
    id: str
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

class JSONAPIResponse(BaseModel):
    meta: Optional[dict] = {}
    data: Optional[JSONAPIResourceObject]
    included: Optional[list[JSONAPIResourceObject]] = []

class JSONAPIResourceIdentifier(BaseModel):
    id: str|int
    type: str

class JSONAPIRelationshipLinks(BaseModel):
    self: str
    related: str

class JSONAPIRelationships(BaseModel):
    links: Optional[JSONAPIRelationshipLinks]
    data: JSONAPIResourceIdentifier

class JSONAPIRequestData(BaseModel):
    data: JSONAPIResourceObject

class JSONAPIRequest(BaseModel):
    data: JSONAPIRequestData
    included: Optional[list[JSONAPIResourceObject]] = []

class Pagination(BaseModel):
    self: str
    first: str
    prev: str
    next: str
    last: str

class Query(BaseModel):
    include: Optional[str] = None
    sort: Optional[str] = None
    fields: Optional[str] = None
    filter: Optional[str] = None
    page: Optional[str] = None

