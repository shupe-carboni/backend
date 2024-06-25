"""
The pydantic models for primary resoureces are all of the same structure, differentiated 
only by the names of the attributes and relationships.
This helper function will take the SQLAlchemy model given to it, and dynamically
generate the pydantic models from it. The text will be saved as a new .py file.

Likewise, the FastAPI routes, specifically GET routes, are well-structured. This file
also generates code for those resources.

Some customization is still required after file generation for imports, 
related resource routes, and POST, PATCH, and DELETE routes.
"""

import re
import os
from sys import argv
from pathlib import Path
from importlib import import_module
from sqlalchemy.inspection import inspect


def create_pydantic_models_for_routes(
    vendor_id: str, sqla_base_model_name: str
) -> tuple[str, str]:
    sqla_model_objs = import_module("app.jsonapi.sqla_models")
    sqla_model = sqla_model_objs.__dict__[sqla_base_model_name]
    if tn := getattr(sqla_model, "__tablename_alt__", None):
        tablename = tn
    else:
        tablename = sqla_model.__tablename__

    model = inspect(sqla_model)
    columns = model.columns
    relationships = model.relationships

    attrs_columns = [
        (col.name, col.type.python_type.__name__)
        for col in columns
        if not col.foreign_keys and not col.primary_key
    ]
    rels_columns = [(rel, rel.replace("_", "-")) for rel in relationships.keys()]

    attrs = "\n    ".join(
        [
            f"{name}: Optional[{_type}] = Field(default=None, alias=\"{name.replace('_','-')}\")"
            for name, _type in attrs_columns
        ]
    )
    filters = "\n    ".join(
        [
            f"filter_{name}: str = Field(default=None, alias=\"filter[{name.replace('_','-')}]\")"
            for name, _type in attrs_columns
        ]
    )
    rels = "\n    ".join(
        [
            f'{sc_name}: Optional[JSONAPIRelationships] = Field(default=None, alias="{kc_name}")'
            for sc_name, kc_name in rels_columns
        ]
    )
    fields = "\n    ".join(
        [
            f'fields_{sc_name}: str = Field(default=None, alias="fields[{kc_name}]")'
            for sc_name, kc_name in rels_columns
        ]
    )
    fields += f"\n    fields_{tablename}: str = Field(default=None, alias=\"fields[{tablename.replace('_','-')}]\")"
    imports = """
from pydantic import BaseModel, Field, create_model, ConfigDict
from typing import Optional
from app.jsonapi.core_models import (
    JSONAPIResourceIdentifier,
    JSONAPIRelationshipsResponse,
    JSONAPIRelationships,
    JSONAPIResponse,
    Query,
)
    """
    template = f"""
from app.jsonapi.sqla_models import {sqla_base_model_name}


class {sqla_base_model_name}RID(JSONAPIResourceIdentifier):
    type: str = {sqla_base_model_name}.__jsonapi_type_override__


class {sqla_base_model_name}RelResp(JSONAPIRelationshipsResponse):
    data: list[{sqla_base_model_name}RID] | {sqla_base_model_name}RID


class {sqla_base_model_name}Attrs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    {attrs}


class {sqla_base_model_name}Rels(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    {rels}


class {sqla_base_model_name}Filters(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    {filters}


class {sqla_base_model_name}Fields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    {fields}


class {sqla_base_model_name}RObj({sqla_base_model_name}RID):
    attributes: {sqla_base_model_name}Attrs
    relationships: {sqla_base_model_name}Rels


class {sqla_base_model_name}Resp(JSONAPIResponse):
    data: list[{sqla_base_model_name}RObj] | {sqla_base_model_name}RObj


class Related{sqla_base_model_name}Resp({sqla_base_model_name}Resp):
    included: dict = {{}}
    links: Optional[dict] = Field(default=None, exclude=True)


_{sqla_base_model_name}Query: type[BaseModel] = create_model(
    "{sqla_base_model_name}Query",
    **{{
        field: (field_info.annotation, field_info)
        for field, field_info in Query.model_fields.items()
    }},
    **{{
        f"fields_{{field}}": (Optional[str], None)
        for field in {sqla_base_model_name}Rels.model_fields.keys()
    }},
    **{{
        f"filter_{{field}}": (Optional[str], None)
        for field in {sqla_base_model_name}Attrs.model_fields.keys()
    }},
    **{{
        f'fields_{tablename}': (
            Optional[str],
            None,
        )
    }},
)


class {sqla_base_model_name}Query(_{sqla_base_model_name}Query, BaseModel): ...


class {sqla_base_model_name}QueryJSONAPI({sqla_base_model_name}Fields, {sqla_base_model_name}Filters, Query):
    page_number: Optional[int] = Field(default=None, alias="page[number]")
    page_size: Optional[int] = Field(default=None, alias="page[size]")
"""
    if not os.path.exists(f"./app/{vendor_id}/models.py"):
        template = imports + template
    if fields := sqla_model.__modifiable_fields__:
        mod_attrs_columns = [
            (col.name, col.type.python_type.__name__)
            for col in columns
            if not col.foreign_keys and not col.primary_key and col.name in fields
        ]
        mod_attrs = "\n    ".join(
            [
                f"{name}: Optional[{_type}] = Field(default=None, alias=\"{name.replace('_','-')}\")"
                for name, _type in mod_attrs_columns
            ]
        )
        mod = f"""

class Mod{sqla_base_model_name}Attrs(BaseModel):
    {mod_attrs}
     
class Mod{sqla_base_model_name}RObj(BaseModel):
    id: int
    type: str = {sqla_base_model_name}.__jsonapi_type_override__
    attributes: Mod{sqla_base_model_name}Attrs
    relationships: {sqla_base_model_name}Rels
    
class Mod{sqla_base_model_name}(BaseModel):
    data: Mod{sqla_base_model_name}RObj
        """
        template += mod

    return "models.py", template


def create_fastapi_routes(vendor_id: str, sqla_base_model_name: str) -> str:
    tablename: str
    sqla_model_objs = import_module("app.jsonapi.sqla_models")
    sqla_model = sqla_model_objs.__dict__[sqla_base_model_name]
    if tn := getattr(sqla_model, "__tablename_alt__", None):
        tablename = tn
    else:
        tablename = sqla_model.__tablename__

    model = inspect(sqla_model)
    relationships = model.relationships
    # snake case and kebab case respectively
    rels_columns = [(rel, rel.replace("_", "-")) for rel in relationships.keys()]

    depluraled = tablename[:-1] if tablename.endswith("s") else tablename
    # make camelcase
    ops_name_prefix = re.sub(r"[^A-Za-z]", " ", vendor_id).title().replace(" ", "")

    template = f"""
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.{vendor_id}.models import (
    {sqla_base_model_name}Resp,
    {sqla_base_model_name}Query,
    {sqla_base_model_name}QueryJSONAPI,
)
from app.jsonapi.sqla_models import {sqla_base_model_name}

PARENT_PREFIX = "/vendors/{vendor_id}"
{tablename.upper()} = {sqla_base_model_name}.__jsonapi_type_override__

{tablename} = APIRouter(
    prefix=f"/{{{tablename.upper()}}}", tags=["{vendor_id}", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query({sqla_base_model_name}QueryJSONAPI)


@{tablename}.get(
    "",
    response_model={sqla_base_model_name}Resp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def {depluraled}_collection(
    token: Token, session: NewSession, query: {sqla_base_model_name}Query = Depends()
) -> {sqla_base_model_name}Resp:
    return (
        auth.{ops_name_prefix}Operations(token, {sqla_base_model_name}, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@{tablename}.get(
    "/{{{depluraled}_id}}",
    response_model={sqla_base_model_name}Resp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def {depluraled}_resource(
    token: Token,
    session: NewSession,
    {depluraled}_id: int,
    query: {sqla_base_model_name}Query = Depends(),
) -> {sqla_base_model_name}Resp:
    return (
        auth.{ops_name_prefix}Operations(token, {sqla_base_model_name}, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), {depluraled}_id)
    )

"""
    for sc_name, kc_name in rels_columns:
        related_resource = f"""
@{tablename}.get(
    "/{{{depluraled}_id}}/{kc_name}",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def {depluraled}_related_{sc_name}(
    token: Token,
    session: NewSession,
    {depluraled}_id: int,
    query: {sqla_base_model_name}Query = Depends(),
) -> None:
    return (
        auth.{ops_name_prefix}Operations(token, {sqla_base_model_name}, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), {depluraled}_id, "{kc_name}")
    )

@{tablename}.get(
    "/{{{depluraled}_id}}/relationships/{kc_name}",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def {depluraled}_relationships_{sc_name}(
    token: Token,
    session: NewSession,
    {depluraled}_id: int,
    query: {sqla_base_model_name}Query = Depends(),
) -> None:
    return (
        auth.{ops_name_prefix}Operations(token, {sqla_base_model_name}, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), {depluraled}_id, "{kc_name}", True)
    )

    """
        template += related_resource

    if sqla_model.__modifiable_fields__:
        primary_id_ref_plural: str = sqla_model.__primary_ref__
        primary_id_ref = (
            primary_id_ref_plural[:-1]
            if primary_id_ref_plural and primary_id_ref_plural.endswith("s")
            else primary_id_ref_plural
        )
        patch = f"""

from app.{vendor_id}.models import Mod{sqla_base_model_name}

@{tablename}.patch(
    "/{{{depluraled}_id}}",
    response_model={sqla_base_model_name}Resp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_{depluraled}(
    token: Token,
    session: NewSession,
    {depluraled}_id: int,
    mod_data: Mod{sqla_base_model_name},
) -> {sqla_base_model_name}Resp:
    return (
        auth.{ops_name_prefix}Operations(token, {sqla_base_model_name}, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id={depluraled}_id,
    """
        if primary_id_ref:
            patch += (
                " " * 3 * 4
                + f"""primary_id=mod_data.data.relationships.{primary_id_ref_plural}.data.id
            )
        )

        """
            )
        else:
            patch += f"""
            )
        )

        """
        template += patch
    delete = f"""
@{tablename}.delete(
    "/{{{depluraled}_id}}",
    tags=["jsonapi"],
)
async def del_{depluraled}(
    token: Token,
    session: NewSession,
    {depluraled}_id: int,
    {primary_id_ref}_id: int,
) -> None:
    return (
        auth.{ops_name_prefix}Operations(token, {sqla_base_model_name}, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id={depluraled}_id, primary_id={primary_id_ref}_id)
    )
    """
    delete = delete.replace("None_id: int,", "")
    delete = delete.replace(", primary_id=None_id)", ")")
    template += delete

    return f"{tablename}.py", template


def save_as_py_file(dir: str, filename: str, text: str) -> None:
    path = Path("./app") / dir / filename
    if os.path.exists(path) and "models" in filename:
        mode = "a"
    else:
        mode = "w"
    with open(path, mode) as new_file:
        new_file.write(text)


if __name__ == "__main__":
    vendor_id = argv[-2]
    sqla_model_name = argv[-1]
    try:
        save_as_py_file(
            vendor_id, *create_pydantic_models_for_routes(vendor_id, sqla_model_name)
        )
    except Exception as e:
        print("file creation failed")
        print(e)
    else:
        save_as_py_file(
            vendor_id + "/routes", *create_fastapi_routes(vendor_id, sqla_model_name)
        )
