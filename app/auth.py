import os
import time
import requests
import bcrypt
from abc import ABC
from enum import Enum, IntEnum, StrEnum, auto
from hashlib import sha256
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()
from pydantic import BaseModel, field_validator
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from jose.jwt import get_unverified_header, decode

from typing import Optional, Callable, Literal, TYPE_CHECKING
import collections.abc as collections
from functools import partial
from sqlalchemy import text, Column
from sqlalchemy_jsonapi.errors import ResourceNotFoundError, BadRequestError
from sqlalchemy_jsonapi.serializer import JSONAPIResponse
from app.jsonapi.sqla_jsonapi_ext import SQLAlchemyModel
from app.db.db import Session
from app.jsonapi.sqla_models import (
    serializer,
    serializer_partial,
    SCACustomer,
    SCAVendor,
    ADPCustomer,
    ADPQuote,
    permitted_customer_location_ids,
    Vendor,
    VendorsAttr,
    VendorProduct,
    VendorPricingClass,
    VendorPricingByClass,
    VendorPricingByCustomer,
    VendorCustomer,
    VendorCustomerAttr,
    VendorProductClassDiscount,
    VendorQuote,
    VendorQuoteProduct,
)
from app.jsonapi.sqla_jsonapi_ext import GenericData

if TYPE_CHECKING:
    from app.jsonapi.sqla_models import JSONAPI_


token_auth_scheme = HTTPBearer()
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
ALGORITHMS = os.getenv("ALGORITHMS")
AUDIENCE = os.getenv("AUDIENCE")


class TUI(Enum):
    SCA_CLOUD = os.getenv("SCA_CLOUD_TUI_CLIENT_ID")
    DEVELOPER = os.getenv("DEVELOPER_TUI_CLIENT_ID")


class UserTypes(StrEnum):
    developer = auto()
    sca_admin = auto()
    sca_employee = auto()
    customer_admin = auto()
    customer_manager = auto()
    customer_std = auto()
    view_only = auto()


class Permissions(IntEnum):
    sca_admin = 31
    sca_employee = 30
    developer = 20
    customer_admin = 12
    customer_manager = 11
    customer_std = 10
    view_only = 1


class VerifiedToken(BaseModel):
    """
    Representing a verified token by the hash of the token itself
    along with expiry time and permissions in order to check
    whether or not token should be used and how it can be used.

    This will representation will be used in an in-memory storage
    system called LocalTokenStore, which will keep a set of
    VerifiedTokens and check for the incoming token in the
    collection.
    """

    token: bytes
    exp: int
    permissions: IntEnum
    nickname: str
    name: str
    email: str
    email_verified: bool

    def is_expired(self) -> bool:
        return time.time() > self.exp

    @field_validator("token", mode="before")
    def hash_token(cls, value: str):
        token_b = value.encode("utf-8")
        token_256_hash = sha256(token_b).digest()
        salt = bcrypt.gensalt(12)
        return bcrypt.hashpw(token_256_hash, salt)

    def __hash__(self) -> int:
        return self.token.__hash__()

    def is_same_token(self, other: str) -> bool:
        other_b = other.encode("utf-8")
        other_sha_256 = sha256(other_b).digest()
        return bcrypt.checkpw(other_sha_256, self.token)


class LocalTokenStore:
    """Global in-memory storage system for access tokens"""

    tokens: set[VerifiedToken] = set()

    @classmethod
    def add_token(cls, new_token: VerifiedToken) -> None:
        cls.tokens.add(new_token)

    @classmethod
    def contains(cls, token: str) -> VerifiedToken | None:
        for verified_token in cls.tokens:
            if verified_token.is_same_token(token):
                if not verified_token.is_expired():
                    return verified_token
        return


def get_user_info(access_token: str) -> dict:
    user_info_ep = AUTH0_DOMAIN + "/userinfo"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    user_info = requests.get(user_info_ep, headers=auth_header)
    if 299 >= user_info.status_code >= 200:
        user_info = user_info.json()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user could not be verified",
        )
    match user_info:
        case {"nickname": a, "name": b, "email": c, "email_verified": d, **other}:
            return {"nickname": a, "name": b, "email": c, "email_verified": d}
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user could not be verified",
            )


def set_permissions(permissions: list[str]) -> IntEnum:
    if not permissions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    elif len(permissions) > 1:
        vals = []
        for perm in permissions:
            perm = perm.replace("-", "_")
            perm_obj = Permissions[perm]
            vals.append(perm_obj)
        return min(vals)
    else:
        return Permissions[permissions[0].replace("-", "_")]


async def authenticate_auth0_token(
    token: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
) -> VerifiedToken:
    error = None
    if verified_token := LocalTokenStore.contains(token.credentials):
        return verified_token
    jwks = requests.get(AUTH0_DOMAIN + "/.well-known/jwks.json").json()
    try:
        unverified_header = get_unverified_header(token.credentials)
    except Exception as err:
        error = err
    else:
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
        if rsa_key:
            try:
                payload = decode(
                    token.credentials, rsa_key, algorithms=ALGORITHMS, audience=AUDIENCE
                )
            except Exception as err:
                error = err
            else:
                client_id: str = payload["azp"]
                match client_id:
                    case TUI.SCA_CLOUD.value:
                        user_info = dict(
                            nickname="SCA Cloud TUI",
                            name="SCA Cloud TUI",
                            email="",
                            email_verified=True,
                        )
                    case TUI.DEVELOPER.value:
                        user_info = dict(
                            nickname="Developer TUI",
                            name="Developer TUI",
                            email=os.getenv("TEST_USER_EMAIL"),
                            email_verified=True,
                        )
                    case _:
                        user_info = get_user_info(token.credentials)
                verified_token = VerifiedToken(
                    token=token.credentials,
                    exp=payload["exp"],
                    permissions=set_permissions(payload["permissions"]),
                    **user_info,
                )
                LocalTokenStore.add_token(new_token=verified_token)
                return verified_token
        else:
            error = "No RSA key found in JWT Header"
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))


class UnverifiedEmail(Exception): ...


class IDsNotAssociated(Exception): ...


class IDNotAssociatedWithUser(Exception): ...


class InvalidArguments(Exception): ...


def standard_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UnverifiedEmail:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="Email not verified"
            )
        except ResourceNotFoundError:
            raise HTTPException(status.HTTP_204_NO_CONTENT)
        except IDNotAssociatedWithUser:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Primary ID is not associated with the user",
            )
        except IDsNotAssociated:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Object ID not associated with the Primary ID",
            )
        except InvalidArguments as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
        except HTTPException as e:
            raise e
        except BadRequestError as e:
            raise HTTPException(e.status_code, e.detail)
        except:
            import traceback as tb

            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, detail=pprint(tb.format_exc())
            )

    return wrapper


def check_object_id_association(
    session: Session,
    primary_reference_resource: str,
    primary_reference_id: int,
    resource: str,
    obj_id: int | str | None,
) -> None:
    """Make sure the oject id passed in is associated with the the id of the primary
    reference, usually pulled from the payload of a POST, PATCH, or DELETE request,
    more specifically, the id contained in the relationships object."""
    if obj_id:
        current_obj = serializer.get_resource(
            session, {"include": primary_reference_resource}, resource, obj_id, True
        )
        if (
            current_obj["data"]["relationships"][primary_reference_resource]["data"][
                "id"
            ]
            != primary_reference_id
        ):
            raise IDsNotAssociated


class SecOp(ABC):
    """Abstract Base Class for vendor specific routes for handiling HTTP requests.

    Each route type implements this class and calls the allow-listing methods
    in each route.

    allow_* methods are called explicitly in each route implementation to allow-list
    them when sufficient permissions are present (ex: .allow_admin() will execute
    the check to see if the token has admin permissions and change the state of
    self._admin to True)

    Customer Location ("Branch") id is universal for gating GET requests. For the rest,
    each resource should refer to it's own table of primary IDs (usually customers but
    not always, such as in the case of ADP Quotes) using
    "permitted_primary_resource_ids" to properly gate POST, PATCH, and DELETE requests.

    """

    def __init__(
        self, token: VerifiedToken, resource: SQLAlchemyModel, **kwargs
    ) -> None:
        if not token.email_verified:
            raise UnverifiedEmail
        self.token = token
        # for permission whitelisting
        self._admin = False
        self._sca = False
        self._dev = False
        self._customer = False
        # resource definitions
        self._resource = resource
        self._primary_resource: SQLAlchemyModel
        self._associated_resource: bool
        self._serializer: JSONAPI_
        self.filters: dict = kwargs

    def permitted_primary_resource_ids(
        self, session: Session
    ) -> tuple[Column, set[int]]:
        primary_id_col, queries = self._resource.permitted_primary_resource_ids(
            self.token.email, **self.filters
        )
        return primary_id_col, self.get_result_from_id_association_queries(
            session,
            **queries,
            **self.filters,
        )

    def permitted_customer_location_ids(self, session: Session) -> set[int]:
        return self.get_result_from_id_association_queries(
            session,
            **permitted_customer_location_ids(email=self.token.email),
            **self.filters,
        )

    def get_result_from_id_association_queries(
        self,
        session: Session,
        sql_admin: str,
        sql_manager: str,
        sql_user_only: str,
        **filters,
    ) -> set[int]:
        queries = [sql_admin, sql_manager, sql_user_only]
        if not all(queries):
            raise Exception("all user type sql queries must be defined")
        match UserTypes[self.token.permissions.name]:
            case UserTypes.customer_std:
                queries.remove(sql_admin)
                queries.remove(sql_manager)
            case UserTypes.customer_manager:
                queries.remove(sql_admin)
            case UserTypes.customer_admin | UserTypes.developer:
                pass
            case UserTypes.sca_employee | UserTypes.sca_admin:
                # TODO
                # SET UP QUERY OPTION FOR SCA, USED FOR FILTERING COLLECTIONS BY VENDOR 
                pass
            case _:
                raise Exception("invalid select_type")

        filters_suffixed = {k + "_1": v for k, v in filters.items()}
        for sql in queries:
            result = session.scalars(
                text(sql), dict(email_1=self.token.email, **filters_suffixed)
            ).all()
            if result:
                return set(result)
        return set()

    def allow_admin(self) -> "SecOp":
        self._admin = self.token.permissions >= Permissions.sca_admin
        return self

    def allow_sca(self) -> "SecOp":
        self._sca = (
            Permissions.sca_admin > self.token.permissions >= Permissions.sca_employee
        )
        return self

    def allow_dev(self) -> "SecOp":
        self._dev = self.token.permissions == Permissions.developer
        return self

    def allow_customer(
        self, level: Literal["admin"] | Literal["manager"] | Literal["std"]
    ) -> "SecOp":
        self._customer = (
            Permissions.customer_admin
            >= self.token.permissions
            >= Permissions[f"customer_{level}"]
        )
        return self

    def gate(
        self,
        session: Session,
        primary_id: Optional[int | str] = None,
        obj_id: Optional[int | str] = None,
    ) -> None:
        if self._associated_resource:
            if not primary_id:
                raise ValueError(
                    "primary_id query argument is required when the"
                    " resource initialized is not the primary key resource"
                )
            check_object_id_association(
                session,
                self._primary_resource.__jsonapi_type_override__,
                primary_id,
                self._resource.__jsonapi_type_override__,
                obj_id,
            )
            if self._admin or self._sca:
                return
            elif self._customer or self._dev:
                _, primary_ids = self.permitted_primary_resource_ids(session=session)
                if primary_id not in primary_ids:
                    raise IDNotAssociatedWithUser
                return
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        else:
            if self._admin or self._sca or self._dev:
                return
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    @standard_error_handler
    def get(
        self,
        session: Session,
        query: dict = {},
        obj_id: Optional[int | str] = None,
        related_resource: Optional[str] = None,
        relationship: bool = False,
        **kwargs,
    ):
        resource = self._resource.__jsonapi_type_override__
        vendor_filter = partial(self.permitted_primary_resource_ids, session=session)
        optional_arguments = (obj_id, relationship, related_resource)
        match optional_arguments:
            case None, False, None:
                result_query = partial(
                    self._serializer.get_collection,
                    session=session,
                    query=query,
                    api_type=resource,
                    vendor_filter=vendor_filter() if self.filters else None,
                )
            case int() | str(), False, None:
                result_query = partial(
                    self._serializer.get_resource,
                    session=session,
                    query=query,
                    api_type=resource,
                    obj_id=obj_id,
                    obj_only=True,
                )
            case int() | str(), False, str():
                result_query = partial(
                    self._serializer.get_related,
                    session=session,
                    query=query,
                    api_type=resource,
                    obj_id=obj_id,
                    rel_key=related_resource,
                )
            case int() | str(), True, str():
                result_query = partial(
                    self._serializer.get_relationship,
                    session=session,
                    query=query,
                    api_type=resource,
                    obj_id=obj_id,
                    rel_key=related_resource,
                )
            case _:
                raise InvalidArguments(
                    "Invalid argument set supplied to auth.secured_get_query"
                )
        if self._admin or self._sca:
            result = result_query()
        elif self._customer or self._dev:
            ids = self.permitted_customer_location_ids(session=session)
            result = result_query(permitted_ids=ids)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        match result:
            case JSONAPIResponse():
                result = result.data
        if not result["data"]:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
        return result

    @standard_error_handler
    def post(
        self,
        session: Session,
        data: dict | Callable,
        obj_id: Optional[int] = None,
        primary_id: Optional[int] = None,
        related_resource: Optional[str] = None,
    ) -> GenericData | None:

        self.gate(session, primary_id, obj_id)

        match data:
            case collections.Callable():
                data: dict = data()

        optional_arguments = (obj_id, related_resource)
        match optional_arguments:
            case None, None:
                operation = partial(
                    self._serializer.post_collection,
                    session=session,
                    data=data,
                    api_type=self._resource.__jsonapi_type_override__,
                )
            case int(), str():
                operation = partial(
                    self._serializer.post_relationship,
                    session=session,
                    json_data=data,
                    api_type=self._resource.__jsonapi_type_override__,
                    obj_id=obj_id,
                    rel_key=related_resource,
                )
            case int(), _:
                # attempted relationship without the primary resource referenced
                raise InvalidArguments("The related resource name is missing")
            case _, str():
                # trying to post a relationship without the id to add
                raise InvalidArguments(
                    "the object id for the primary resource is missing"
                )
            case _:
                raise InvalidArguments(
                    "Invalid argument set. Provide either an object id and related "
                    "object for a relationship or neither to create a new instance of "
                    "the primary reseource."
                )

        result: GenericData | JSONAPIResponse = operation()

        match result:
            case JSONAPIResponse():
                return result.data
            case dict():
                return result

    @standard_error_handler
    def patch(
        self,
        session: Session,
        data: dict | Callable,
        obj_id: int,
        primary_id: Optional[int] = None,
        related_resource: Optional[str] = None,
    ) -> GenericData | None:

        self.gate(session, primary_id, obj_id)
        match data:
            case collections.Callable():
                data: dict = data()

        if related_resource:
            operation = partial(
                self._serializer.patch_relationship,
                session=session,
                json_data=data,
                api_type=self._resource.__jsonapi_type_override__,
                obj_id=obj_id,
                rel_key=related_resource,
            )
        else:
            operation = partial(
                self._serializer.patch_resource,
                session=session,
                json_data=data,
                api_type=self._resource.__jsonapi_type_override__,
                obj_id=obj_id,
            )
        result: GenericData | JSONAPIResponse = operation()

        match result:
            case JSONAPIResponse():
                return result.data
            case dict():
                return result

    @standard_error_handler
    def delete(self, session: Session, obj_id: int, primary_id: Optional[int] = None):
        # TODO create a soft delete version
        self.gate(session, primary_id, obj_id)
        self._serializer.delete_resource(
            session=session,
            data={},
            api_type=self._resource.__jsonapi_type_override__,
            obj_id=obj_id,
        )
        return JSONResponse({}, status_code=204)


class CustomersOperations(SecOp):

    def __init__(
        self, token: VerifiedToken, resource: SQLAlchemyModel, prefix: str = ""
    ) -> None:
        super().__init__(token, resource)
        self._primary_resource = SCACustomer
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix=prefix)


class VendorOperations(SecOp):

    def __init__(
        self, token: VerifiedToken, resource: SQLAlchemyModel, prefix: str = ""
    ) -> None:
        super().__init__(token, resource)
        self._primary_resource = SCAVendor
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix=prefix)

    def permitted_primary_resource_ids(self, session: Session) -> list[int]:
        """The Vendors resource does not have underlying resources that need to
        be gated by user. Customers can only view the info, and only SCA is allowed
        to add, edit, or delete any vendor and its associated information.

        The ids returned are strictly for the developer role, which still gets checked
        for id association to the primary resource (Vendors)"""
        dev_vendor_ids = f"""
            SELECT id
            FROM {self._primary_resource.__tablename__}
            WHERE name LIKE 'RANDOM VENDOR%';
        """
        return session.execute(text(dev_vendor_ids)).scalars().all()

    def post(
        self,
        session: Session,
        data: GenericData | Callable,
        obj_id: int | None = None,
        primary_id: int | None = None,
        related_resource: str | None = None,
    ) -> GenericData | None:
        """enforce the expectation that customers will not be allowed to perform
        this action"""
        if self._customer:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return super().post(session, data, obj_id, primary_id, related_resource)

    def patch(
        self,
        session: Session,
        data: GenericData | Callable,
        obj_id: int,
        primary_id: int | None = None,
        related_resource: str | None = None,
    ) -> GenericData | None:
        """enforce the expectation that customers will not be allowed to perform
        this action"""
        if self._customer:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return super().patch(session, data, obj_id, primary_id, related_resource)

    def delete(self, session: Session, obj_id: int, primary_id: int | None = None):
        """enforce the expectation that customers will not be allowed to perform
        this action"""
        if self._customer:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return super().delete(session, obj_id, primary_id)


class ADPOperations(SecOp):

    def __init__(
        self, token: VerifiedToken, resource: SQLAlchemyModel, prefix: str = ""
    ) -> None:
        super().__init__(token, resource)
        self._primary_resource = ADPCustomer
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


class ADPQuoteOperations(SecOp):

    def __init__(
        self, token: VerifiedToken, resource: SQLAlchemyModel, prefix: str = ""
    ) -> None:
        super().__init__(token, resource)
        self._primary_resource = ADPQuote
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


class AGasOperations(SecOp):
    def __init__(
        self, token: VerifiedToken, resource: SQLAlchemyModel, prefix: str = ""
    ) -> None:
        super().__init__(token, resource)
        self._primary_resource = None
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


class AtcoOperations(SecOp):

    def __init__(
        self, token: VerifiedToken, resource: SQLAlchemyModel, prefix: str = ""
    ) -> None:
        super().__init__(token, resource)
        self._primary_resource = None
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


# V2
class VendorOperations2(SecOp):

    def __init__(
        self,
        token: VerifiedToken,
        resource: SQLAlchemyModel,
        prefix: str = "",
        **filters,
    ) -> None:
        super().__init__(token, resource, **filters)
        self._primary_resource = Vendor
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


class VendorProductOperations(SecOp):

    def __init__(
        self,
        token: VerifiedToken,
        resource: SQLAlchemyModel,
        prefix: str = "",
        **filters,
    ) -> None:
        super().__init__(token, resource, **filters)
        self._primary_resource = VendorProduct
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


class VendorsAttrOperations(SecOp):

    def __init__(
        self,
        token: VerifiedToken,
        resource: SQLAlchemyModel,
        prefix: str = "",
        **filters,
    ) -> None:
        super().__init__(token, resource, **filters)
        self._primary_resource = VendorsAttr
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


class VendorPricingClassOperations(SecOp):

    def __init__(
        self,
        token: VerifiedToken,
        resource: SQLAlchemyModel,
        prefix: str = "",
        **filters,
    ) -> None:
        super().__init__(token, resource, **filters)
        self._primary_resource = VendorPricingClass
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


class VendorPricingByClassOperations(SecOp):

    def __init__(
        self,
        token: VerifiedToken,
        resource: SQLAlchemyModel,
        prefix: str = "",
        **filters,
    ) -> None:
        super().__init__(token, resource, **filters)
        self._primary_resource = VendorPricingByClass
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


class VendorPricingByCustomerOperations(SecOp):

    def __init__(
        self,
        token: VerifiedToken,
        resource: SQLAlchemyModel,
        prefix: str = "",
        **filters,
    ) -> None:
        super().__init__(token, resource, **filters)
        self._primary_resource = VendorPricingByCustomer
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


class VendorCustomerOperations(SecOp):

    def __init__(
        self,
        token: VerifiedToken,
        resource: SQLAlchemyModel,
        prefix: str = "",
        **filters,
    ) -> None:
        super().__init__(token, resource, **filters)
        self._primary_resource = VendorCustomer
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


class VendorCustomerAttrOperations(SecOp):

    def __init__(
        self,
        token: VerifiedToken,
        resource: SQLAlchemyModel,
        prefix: str = "",
        **filters,
    ) -> None:
        super().__init__(token, resource, **filters)
        self._primary_resource = VendorCustomerAttr
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


class VendorProductClassDiscountOperations(SecOp):

    def __init__(
        self,
        token: VerifiedToken,
        resource: SQLAlchemyModel,
        prefix: str = "",
        **filters,
    ) -> None:
        super().__init__(token, resource, **filters)
        self._primary_resource = VendorProductClassDiscount
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


class VendorQuoteOperations(SecOp):

    def __init__(
        self,
        token: VerifiedToken,
        resource: SQLAlchemyModel,
        prefix: str = "",
        **filters,
    ) -> None:
        super().__init__(token, resource, **filters)
        self._primary_resource = VendorQuote
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)


class VendorQuoteProductOperations(SecOp):

    def __init__(
        self,
        token: VerifiedToken,
        resource: SQLAlchemyModel,
        prefix: str = "",
        **filters,
    ) -> None:
        super().__init__(token, resource, **filters)
        self._primary_resource = VendorQuoteProduct
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)
