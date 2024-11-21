from os import getenv
from dotenv import load_dotenv

load_dotenv()
import warnings
from typing import Any
from sqlalchemy_jsonapi import JSONAPI
from fastapi import HTTPException
from sqlalchemy import or_, func, inspect, Column, select
from sqlalchemy.orm import Session, Query as sqlQuery
from sqlalchemy_jsonapi.errors import (
    NotSortableError,
    PermissionDeniedError,
    ResourceTypeNotFoundError,
    ResourceNotFoundError,
    RelationshipNotFoundError,
)
from sqlalchemy_jsonapi.serializer import (
    Permissions,
    JSONAPIResponse,
    check_permission,
    get_rel_desc,
    RelationshipActions,
    MANYTOONE,
    get_permission_test,
    get_attr_desc,
    AttributeActions,
)

QuerySet = dict[str, str]
GenericData = dict[str, dict[str, Any] | list[dict[str, Any]]]


class SQLAlchemyModel:
    """Generic Class representing SQLAlchemy models that pass through
    the serializer"""

    __tablename__: str
    __jsonapi_type__: str
    __jsonapi_type_override__: str
    __jsonapi_map_to_py__: dict[str, str]
    __jsonapi_map_to_api__: dict[str, str]
    id = Column(primary_key=True)

    def apply_customer_location_filtering(
        self, q: sqlQuery, ids: set[int] = None
    ) -> sqlQuery: ...
    def permitted_primary_resource_ids(
        self, email: str, **filters
    ) -> tuple[Column, QuerySet]: ...


DEFAULT_SORT: str = "id"
MAX_PAGE_SIZE: int = 300
MAX_RECORDS: int = 15000
CONTACT_EMAIL: str = getenv("ADMIN_EMAIL")


class JSONAPI_(JSONAPI):
    """
    Custom fixes applied to the JSONAPI object

    _apply_filter static method created to handle filtering arguments.
        This library does not handle filtering.

    _add_pagination adds pagination metadata totalPages and currentPage
        as well as pagination links

    _filter_deleted filters for null values in
        a hard-coded "deleted" column

    __init__  copies the base.registry._class_registry
        attribute under a new attribute named _decl_class_registry
        so that the underlying constructor will work

    get_collection, get_resource, get_related, get_relationship have been overridden
        in order to add unsupported functionality, such as filtering params, sorting,
        pagination, and the ability to work with authentication.

    _fetch_resource and _render_full_resource have also been overridden in support of
        authentication-based filtering of data
    """

    def __init__(self, base, prefix=""):
        self.recurse_depth = 0
        # JSONAPI's constructor is broken for SQLAchelmy 1.4.x
        setattr(base, "_decl_class_registry", base.registry._class_registry)
        super().__init__(base, prefix)

    def _reset_recurse_count(self):
        self.recurse_depth = 0

    def _inc_recurse(self):
        self.recurse_depth += 1

    @staticmethod
    def _apply_filters(
        model: SQLAlchemyModel, sqla_query_obj: sqlQuery, filters: dict[str, str]
    ) -> sqlQuery:
        """
        handler for filter parameters in the query string
        for any value or list of values, this filter is permissive,
        looking for a substring anywhere in the field value that
        matches the arguement(s).
        Roughly equivalent to
            SELECT field
            FROM table
            WHERE field LIKE '%value_1%
            OR LIKE '%value_2%';
        """

        filter_query_args = []
        for field, value in filters.items():
            resource, attr = field
            if field_py := model.__jsonapi_map_to_py__.get(attr):
                model_attr: Column = getattr(model, field_py)
                filter_query_args.append(or_(model_attr.like("%" + value + "%")))
            else:
                warnings.warn(
                    f"Warning: filter field {field} with value {value} was ignored."
                )
        return (
            sqla_query_obj.filter(*filter_query_args)
            if filter_query_args
            else sqla_query_obj
        )

    @staticmethod
    def _filter_deleted(model: SQLAlchemyModel, sqla_query_obj: sqlQuery) -> sqlQuery:
        """
        The 'deleted_at' column signals a soft delete.
        While soft deleting preserves reference integrity,
            we don't want 'deleted_at' values showing up in query results
        """
        field = "deleted_at"
        if model_attr := getattr(model, field, None):
            return sqla_query_obj.filter(model_attr == None)
        else:
            return sqla_query_obj

    @staticmethod
    def _parse_filters(query: dict[str, str]) -> dict[str, list[str]]:
        prefix = "filter["
        field_args = {k: v for k, v in query.items() if k.startswith(prefix)}

        filters = {}

        for k, v in field_args.items():
            k: str
            v: str
            filter_key = k[len(prefix) : -1].split(".")
            match len(filter_key):
                case 1:
                    key_tuple = (None, filter_key.pop())
                case 2:
                    key_tuple = tuple(filter_key)
                case _:
                    raise HTTPException(
                        status_code=400,
                        detail="Relationship filters should be formated [{resource}.{attribute}]"
                        f"\nFilter Argument given: [{'.'.join(filter_key)}]",
                    )

            filters[key_tuple] = v.split(",")

        return filters

    def _add_pagination(
        self, query: dict[str, str], db: Session, resource_name: str, sa_query: sqlQuery
    ) -> tuple[dict, dict]:
        size = MAX_PAGE_SIZE
        offset = 0

        class NoPagination:
            def __init__(self, query: dict[str, str], row_count: int):
                pag_keys = [k for k in query.keys() if k.startswith("page")]
                [query.pop(k) for k in pag_keys]
                self.result = {
                    "meta": {"numRecords": row_count},
                    "links": {
                        "first": "",
                        "last": "",
                    },
                }

            def return_disabled_pagination(self):
                if row_count > MAX_RECORDS:
                    raise HTTPException(
                        status_code=400,
                        detail=f"This request attempted to retrieve "
                        f"{row_count:,}, exceeding the allowed maxiumum: "
                        f"{MAX_RECORDS:,}",
                    )
                return self.result

            def return_one_page(self, link):
                self.result["meta"] |= {
                    "totalPages": 1,
                    "currentPage": 1,
                }
                self.result["links"] = {"first": link, "last": link}
                return self.result

            def return_zero_page(self):
                self.result["meta"] |= {
                    "totalPages": 0,
                    "currentPage": 0,
                }
                return self.result

        row_count: int = db.execute(sa_query.statement).fetchone()[0]
        if row_count == 0:
            return NoPagination(query, row_count).return_zero_page()
        passed_args = {
            k[5:-1]: str(v) for k, v in query.items() if k.startswith("page[")
        }
        link_template = (
            "/{resource_name}" "?page_number={page_num}" "&page_size={page_size}"
        )  # defaulting to number-size
        if passed_args:
            if {"number", "size"} == set(passed_args.keys()):
                number = int(passed_args["number"])
                if number == 0:
                    return NoPagination(query, row_count).return_disabled_pagination()
                size = min(int(passed_args["size"]), MAX_PAGE_SIZE)
                offset = (number - 1) * size
            elif {"limit", "offset"} == set(passed_args.keys()):
                offset = int(passed_args["offset"])
                limit = int(passed_args["limit"])
                size = min(limit, MAX_PAGE_SIZE)
                link_template = (
                    "/{resource_name}" "?page_offset={offset}" "&page_limit={limit}"
                )
            elif {"number"} == set(passed_args.keys()):
                number = int(passed_args["number"])
                if number == 0:
                    return NoPagination(query, row_count).return_disabled_pagination()
                size = MAX_PAGE_SIZE
                offset = (number - 1) * size
            elif {"size"} == set(passed_args.keys()):
                number = 1
                size = min(int(passed_args["size"]), MAX_PAGE_SIZE)
                offset = (number - 1) * size  # == 0

        total_pages = -(row_count // -size)  # ceiling division
        if total_pages == 1:
            link_args = {
                "resource_name": resource_name,
                "page_num": 1,
                "page_size": size,
            }
            return NoPagination(query=query, row_count=row_count).return_one_page(
                link=link_template.format(**link_args)
            )
        else:
            current_page = (offset // size) + 1
            first_page = 1
            last_page = total_pages
            if current_page > last_page:
                current_page = last_page
                offset = (current_page - 1) * size
            next_page = current_page + 1 if current_page != last_page else None
            prev_page = current_page - 1 if current_page != 1 else None
            if "number" in link_template:
                pages = {
                    "first": first_page,
                    "last": last_page,
                    "next": next_page,
                    "prev": prev_page,
                }
                links = {
                    link_name: link_template.format(
                        resource_name=resource_name, page_num=page_val, page_size=size
                    )
                    for link_name, page_val in pages.items()
                    if page_val is not None
                }
                query.update(
                    {
                        # NOTE: This fix feels really wrong .. but it's working.
                        #       Results start on 2nd item without it.
                        "page[number]": str(current_page - 1),
                        "page[size]": str(size),
                    }
                )
            else:
                offsets = {
                    "first": 0,
                    "last": (total_pages - 1) * size,
                    "next": ((next_page - 1) * size if next_page is not None else None),
                    "prev": ((prev_page - 1) * size if prev_page is not None else None),
                }
                links = {
                    link_name: link_template.format(
                        resource_name=resource_name, offset=offset_val, limit=size
                    )
                    for link_name, offset_val in offsets.items()
                    if offset_val is not None
                }
                query.update({"page[offset]": str(offset), "page[limit]": str(size)})

        result_addition = {
            "meta": {
                "totalPages": total_pages,
                "currentPage": current_page,
            },
            "links": links,
        }
        return result_addition

    def get_collection(
        self,
        session: Session,
        query: dict[str, str],
        api_type: str,
        permitted_ids: set[int] = None,
        vendor_filter: tuple[Column, set[int]] = None,
    ) -> GenericData:
        """
        Fetch a collection of resources of a specified type.

        :param session: SQLAlchemy session
        :param query: Dict of query args
        :param api_type: The type of the model

        Override of JSONAPI get_collection - adding filter
            parameter handling after instantation of
            session.query on the 'model'
        """
        model: SQLAlchemyModel = self._fetch_model(api_type=api_type)
        includes_statements = query.get("include", "").split(",")
        includes_models: dict[str, SQLAlchemyModel] = {
            m: self._fetch_model(m)
            for statement in includes_statements
            for m in statement.split(".")
            if statement
        }
        include = self._parse_include(includes_statements)
        fields: dict[str, list[str]] = self._parse_fields(query)
        filters = self._parse_filters(query)
        included = {}
        sorts = query.get("sort", "").split(",")
        order_by = []

        if sorts == [""]:
            sorts = [DEFAULT_SORT]

        collection: sqlQuery = session.query(model)
        collection = self._apply_filters(model, collection, filters)
        collection = self._filter_deleted(model, collection)

        # for pagination, use count query instead of pulling in all
        #   of the data just for a row count
        collection_count: sqlQuery = session.query(func.count(model.id))
        collection_count = self._apply_filters(model, collection_count, filters)
        collection_count = self._filter_deleted(model, collection_count)

        if vendor_filter:
            primary_resource_field, primary_resource_ids = vendor_filter
            collection = collection.filter(
                primary_resource_field.in_(primary_resource_ids)
            )
            collection_count = collection_count.filter(
                primary_resource_field.in_(primary_resource_ids)
            )

        # apply customer-location based filtering
        if permitted_ids:
            collection = model.apply_customer_location_filtering(
                collection, permitted_ids
            )
            collection_count = model.apply_customer_location_filtering(
                collection_count, permitted_ids
            )
        pagination_meta_and_links = self._add_pagination(
            query, session, api_type, collection_count
        )

        for attr in sorts:
            if attr == "":
                break

            attr_name, is_asc = [attr[1:], False] if attr[0] == "-" else [attr, True]

            if (
                attr_name not in model.__mapper__.all_orm_descriptors.keys()
                or not hasattr(model, attr_name)
                or attr_name in model.__mapper__.relationships.keys()
            ):
                return NotSortableError(model, attr_name)

            attr = getattr(model, attr_name)
            if not hasattr(attr, "asc"):
                # pragma: no cover
                return NotSortableError(model, attr_name)

            check_permission(model, attr_name, Permissions.VIEW)

            order_by.append(attr.asc() if is_asc else attr.desc())

        if len(order_by) > 0:
            collection = collection.order_by(*order_by)

        pos = -1
        start, end = self._parse_page(query)
        if end:
            # instead of letting the query pull the entire dataset, use
            # query-level offset and limit if pagination is occuring
            # and from here the start and end will be relative
            # instead of the absolute row positions
            collection = collection.offset(start).limit(end - start + 1)
            end = end - start
            start = 0

        response = JSONAPIResponse()
        response.data["data"] = []
        num_records = 0

        if includes_models:
            includes_permitted_ids = {
                api_type: session.scalars(
                    inc_model.apply_customer_location_filtering(
                        select(inc_model.id), permitted_ids
                    )
                ).all()
                for api_type, inc_model in includes_models.items()
            }
        else:
            includes_permitted_ids = dict()

        for instance in collection:
            try:
                check_permission(instance, None, Permissions.VIEW)
            except PermissionDeniedError:
                continue

            pos += 1
            if end is not None and (pos < start or pos > end):
                continue

            built, rejected = self._render_full_resource(
                instance, include, fields, filters, includes_permitted_ids
            )
            included.update(built.pop("included"))
            response.data["data"].append(built)
            num_records += 1

        response.data["included"] = list(included.values())
        if pagination_meta_and_links:
            pagination_meta_and_links["meta"] |= {"numRecords": num_records}
            response.data.update(pagination_meta_and_links)
        return response.data

    def get_resource(
        self,
        session: Session,
        query: dict[str, str],
        api_type: str,
        obj_id: int,
        obj_only: bool = False,
        permitted_ids: set[int] = None,
    ) -> JSONAPIResponse | GenericData:
        """
        Fetch a resource.

        This customized version adds a parameter for filtering results
        to pass to _fetch_resource()

        :param session: SQLAlchemy session
        :param query: Dict of query args
        :param api_type: Type of the resource
        :param obj_id: ID of the resource
        """
        resource = self._fetch_resource(
            session, api_type, obj_id, Permissions.VIEW, permitted_ids
        )
        includes_statements = query.get("include", "").split(",")
        includes_models: dict[str, SQLAlchemyModel] = {
            m: self._fetch_model(m)
            for statement in includes_statements
            for m in statement.split(".")
            if statement
        }
        include = self._parse_include(includes_statements)
        fields = self._parse_fields(query)
        filters = self._parse_filters(query)
        response = JSONAPIResponse()
        if includes_models:
            includes_permitted_ids = {
                api_type: set(
                    session.scalars(
                        inc_model.apply_customer_location_filtering(
                            select(inc_model.id), permitted_ids
                        )
                    ).all()
                )
                for api_type, inc_model in includes_models.items()
            }
        else:
            includes_permitted_ids = dict()

        built, _ = self._render_full_resource(
            resource, include, fields, filters, includes_permitted_ids
        )
        response.data["included"] = list(built.pop("included").values())

        response.data["data"] = built
        if obj_only:
            return response.data
        else:
            return response

    def get_related(
        self,
        session: Session,
        query: dict,
        api_type: str,
        obj_id: int,
        rel_key: str,
        permitted_ids: set[int] = None,
    ) -> JSONAPIResponse:
        """
        Fetch a collection of related resources.

        Customization to allow passing of permitted id
            numbers to _fetch_resource()

        :param session: SQLAlchemy session
        :param query: Dict of query args
        :param api_type: Type of the resource
        :param obj_id: ID of the resource
        :param rel_key: Key of the relationship to fetch
        """
        resource: SQLAlchemyModel = self._fetch_resource(
            session, api_type, obj_id, Permissions.VIEW, permitted_ids
        )
        if rel_key not in resource.__jsonapi_map_to_py__.keys():
            raise RelationshipNotFoundError(resource, resource, rel_key)
        py_key = resource.__jsonapi_map_to_py__[rel_key]
        relationship = self._get_relationship(resource, py_key, Permissions.VIEW)
        response = JSONAPIResponse()
        related = get_rel_desc(resource, relationship.key, RelationshipActions.GET)(
            resource
        )
        # apply model filtering to the related resource
        rel_key_model: SQLAlchemyModel = self._fetch_model(rel_key)
        rel_key_id_query = select(rel_key_model.id)
        rel_key_permitted_ids = session.scalars(
            rel_key_model.apply_customer_location_filtering(
                rel_key_id_query, permitted_ids
            )
        ).all()
        permitted_ids_obj = {rel_key: set(rel_key_permitted_ids)}
        if relationship.direction == MANYTOONE:
            try:
                if related is None:
                    response.data["data"] = None
                elif related.id not in permitted_ids_obj[related.__jsonapi_type__]:
                    response.data["data"] = None
                else:
                    response.data["data"], _ = self._render_full_resource(
                        related, {}, {}, {}, permitted_ids_obj
                    )
            except PermissionDeniedError:
                response.data["data"] = None
        else:
            response.data["data"] = []
            for item in related:
                if item.id not in permitted_ids_obj[item.__jsonapi_type__]:
                    continue
                try:
                    response.data["data"].append(
                        self._render_full_resource(item, {}, {}, {}, permitted_ids_obj)[
                            0
                        ]
                    )
                except PermissionDeniedError:
                    continue
        return response

    def get_relationship(
        self,
        session: Session,
        query: dict,
        api_type: str,
        obj_id: int,
        rel_key: str,
        permitted_ids: set[int] = None,
    ) -> JSONAPIResponse:
        """
        Fetch a collection of related resource types and ids.

        This customized version adds a parameter for filtering results
        to pass to _fetch_resource()

        :param session: SQLAlchemy session
        :param query: Dict of query args
        :param api_type: Type of the resource
        :param obj_id: ID of the resource
        :param rel_key: Key of the relationship to fetch
        """
        resource = self._fetch_resource(
            session, api_type, obj_id, Permissions.VIEW, permitted_ids
        )
        if rel_key not in resource.__jsonapi_map_to_py__.keys():
            raise RelationshipNotFoundError(resource, resource, rel_key)
        py_key = resource.__jsonapi_map_to_py__[rel_key]
        relationship = self._get_relationship(resource, py_key, Permissions.VIEW)
        response = JSONAPIResponse()

        related = get_rel_desc(resource, relationship.key, RelationshipActions.GET)(
            resource
        )

        # apply filtering to the related model as well
        rel_key_model: SQLAlchemyModel = self._fetch_model(rel_key)
        rel_key_id_query = select(rel_key_model.id)
        rel_key_permitted_ids = set(
            session.scalars(
                rel_key_model.apply_customer_location_filtering(
                    rel_key_id_query, permitted_ids
                )
            ).all()
        )

        if relationship.direction == MANYTOONE:
            if related is None:
                response.data["data"] = None
            elif related.id not in rel_key_permitted_ids:
                response.data["data"] = None
            else:
                try:
                    response.data["data"] = self._render_short_instance(related)
                except PermissionDeniedError:
                    response.data["data"] = None
        else:
            response.data["data"] = []
            for item in related:
                if item.id not in rel_key_permitted_ids:
                    continue
                try:
                    response.data["data"].append(self._render_short_instance(item))
                except PermissionDeniedError:
                    continue

        return response

    def _fetch_resource(
        self,
        session: Session,
        api_type: str,
        obj_id: int,
        permission,
        permitted_ids: set[int] = None,
    ) -> SQLAlchemyModel | None:
        """
        Fetch a resource by type and id, also doing a permission check.

        Custom override in order to apply customer location
        based filtering before fetching the resource, so that
        a customer user cannot possibly fetch a resource
        that they are not allowed to access.

        :param session: SQLAlchemy session
        :param api_type: The type
        :param obj_id: ID for the resource
        :param permission: Permission to check
        """
        if api_type not in self.models.keys():
            raise ResourceTypeNotFoundError(api_type)
        model: SQLAlchemyModel = self.models[api_type]
        if permitted_ids:
            preflight = session.query(model)
            preflight: sqlQuery = model.apply_customer_location_filtering(
                preflight, permitted_ids
            )
            pk = inspect(model).primary_key[0].name
            permitted_object_ids = set([getattr(result, pk) for result in preflight])
            if obj_id in permitted_object_ids:
                obj: SQLAlchemyModel = session.get(model, obj_id)
            else:
                obj = None
        else:
            obj = session.get(model, obj_id)

        if obj is None:
            raise ResourceNotFoundError(model, obj_id)
        check_permission(obj, None, permission)
        return obj

    def _render_full_resource(
        self,
        instance: SQLAlchemyModel,
        include: dict[str, str],
        fields: dict[str, list[str]],
        filters: dict[tuple[str | None, str], list[str]],
        permitted_ids: dict[str, set[int]],
    ) -> tuple[dict[str, dict | str | int], bool]:
        """
        Generate a representation of a full resource to match JSON API spec.

        :param instance: The instance to serialize
        :param include: Dictionary of relationships to include
        :param fields: Dictionary of fields to filter
        -- Custom
        :param permitted_ids: Dict of permitted resource ids by resource

        Permitted ids are used to recursively filter the includes, preventing potential
        improper data exposure.
        """
        api_type = instance.__jsonapi_type__
        orm_desc_keys = instance.__mapper__.all_orm_descriptors.keys()
        attributes = {}
        relationships = {}
        included = {}
        attrs_to_ignore = {"__mapper__", "id"}

        to_ret = dict(
            id=instance.id,
            type=api_type,
            attributes=attributes,
            relationships=relationships,
            included=included,
        )

        if api_type in fields.keys():
            local_fields = [instance.__jsonapi_map_to_py__[x] for x in fields[api_type]]
        else:
            local_fields = orm_desc_keys

        for key, relationship in instance.__mapper__.relationships.items():
            attrs_to_ignore |= set([c.name for c in relationship.local_columns]) | {key}
            api_key = instance.__jsonapi_map_to_api__[key]
            try:
                desc = get_rel_desc(instance, key, RelationshipActions.GET)
            except PermissionDeniedError:
                continue

            if relationship.direction == MANYTOONE:
                if key in local_fields:
                    relationships[api_key] = {
                        "links": self._lazy_relationship(api_type, instance.id, api_key)
                    }

                if api_key in include.keys():
                    related_item: SQLAlchemyModel = desc(instance)

                    reject_instance = False
                    for filter in filters:
                        resource, attr = filter
                        if api_key == resource:
                            if attr_value := getattr(related_item, attr, None):
                                if attr_value not in filters[filter]:
                                    reject_instance = True
                    if reject_instance:
                        return to_ret, reject_instance

                    is_deleted = getattr(related_item, "deleted_at", None) is not None
                    not_permitted = False
                    if permitted_ids and related_item:
                        not_permitted = (
                            related_item.id
                            not in permitted_ids[related_item.__jsonapi_type__]
                        )
                    if not_permitted or is_deleted:
                        relationships[api_key]["data"] = None
                        continue

                    if related_item is not None:
                        perm = get_permission_test(related_item, None, Permissions.VIEW)
                    if key in local_fields and (
                        related_item is None or not perm(related_item)
                    ):
                        relationships[api_key]["data"] = None
                        continue
                    if key in local_fields:
                        relationships[api_key]["data"] = self._render_short_instance(
                            related_item
                        )  # NOQA
                    new_include = self._parse_include(include[api_key])
                    built, rejected = self._render_full_resource(
                        related_item, new_include, fields, filters, permitted_ids
                    )
                    if not rejected:
                        built_included = built.pop("included")
                        included.update(built_included)
                        built_incl_key = (
                            related_item.__jsonapi_type__,
                            related_item.id,
                        )
                        included[built_incl_key] = built  # NOQA
            else:
                if key in local_fields:
                    relationships[api_key] = {
                        "links": self._lazy_relationship(
                            api_type, instance.id, api_key
                        ),
                    }

                if api_key not in include.keys():
                    continue

                if key in local_fields:
                    relationships[api_key]["data"] = []

                related: list[SQLAlchemyModel] = desc(instance)

                ## reapply filtering if filtering was used for the query on the
                ## primary resource
                if permitted_ids:
                    related = [
                        item
                        for item in related
                        if item.id in permitted_ids[item.__jsonapi_type__]
                        and getattr(item, "deleted_at", None) is None
                    ]
                for item in related:
                    try:
                        check_permission(item, None, Permissions.VIEW)
                    except PermissionDeniedError:
                        continue

                    reject_related_item = False
                    for filter in filters:
                        resource, attr = filter
                        if api_key == resource:
                            if attr_value := getattr(item, attr, None):
                                if attr_value not in filters[filter]:
                                    reject_related_item = True

                    if reject_related_item:
                        continue

                    if key in local_fields:
                        relationships[api_key]["data"].append(
                            self._render_short_instance(item)
                        )
                    new_include = self._parse_include(include[api_key])
                    built, rejected = self._render_full_resource(
                        item, new_include, fields, filters, permitted_ids
                    )
                    if not rejected:
                        built_included = built.pop("included")
                        built_incl_key = (item.__jsonapi_type__, item.id)
                        included.update(built_included)
                        included[built_incl_key] = built  # NOQA

        for key in set(orm_desc_keys) - attrs_to_ignore:
            try:
                desc = get_attr_desc(instance, key, AttributeActions.GET)
                if key in local_fields:
                    py_key = instance.__jsonapi_map_to_api__[key]
                    attributes[py_key] = desc(instance)  # NOQA
            except PermissionDeniedError:
                continue

        return to_ret, False
