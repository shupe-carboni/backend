import os
import time
import requests
import threading
from datetime import datetime
from abc import ABC
from enum import Enum, IntEnum, StrEnum, auto
from hashlib import sha256
from dotenv import load_dotenv
from logging import getLogger

load_dotenv()
from pydantic import BaseModel, field_validator
from fastapi import Depends, HTTPException, status, Response, Header
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
from sqlalchemy_jsonapi.errors import ValidationError

if TYPE_CHECKING:
    from app.jsonapi.sqla_models import JSONAPI_

logger = getLogger("uvicorn.info")

token_auth_scheme = HTTPBearer()
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
ALGORITHMS = os.getenv("ALGORITHMS")
AUDIENCE = os.getenv("AUDIENCE")


class TUI(Enum):
    SCA_CLOUD = os.getenv("SCA_CLOUD_TUI_CLIENT_ID")
    DEVELOPER = os.getenv("DEVELOPER_TUI_CLIENT_ID")
    MS_POWER_AUTOMATE = os.getenv("MS_AUTOMATE_CLIENT_ID")


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
    hardcast_confirmations = 2
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

    token: str
    exp: int
    permissions: IntEnum
    sim_permissions: IntEnum = Permissions.customer_admin
    nickname: str
    name: str
    email: str
    email_verified: bool

    def is_expired(self) -> bool:
        return time.time() > self.exp

    @field_validator("token", mode="before")
    def hash_token(cls, value: str) -> str:
        token_b = value.encode("utf-8")
        token_256 = sha256(token_b)
        return token_256.hexdigest()

    def set_simulated_permissions(self, perm: int) -> None:
        top_range = Permissions.customer_admin
        bottom_range = Permissions.customer_std
        out_of_range = not (bottom_range <= perm <= top_range)
        if out_of_range:
            range_ = f"Simulated permission range = [{bottom_range}, {top_range}]"
            available_perms = [
                repr(p) for p in Permissions if bottom_range <= p <= top_range
            ]
            raise HTTPException(
                400,
                detail={
                    "simulated_permissions": {
                        "range": range_,
                        "defined": available_perms,
                    }
                },
            )

        if not self.permissions == Permissions.developer:
            raise HTTPException(
                400, "Cannot set simulated permissions unless you are a developer."
            )
        try:
            perm = Permissions(perm)
        except Exception:
            # set at the nearest permission lower than target value given
            perm = max(
                (p for p in Permissions if p.value < perm),
                key=lambda k: Permissions(k).value,
                default=Permissions.customer_std,
            )
        if perm != Permissions.developer:
            self.sim_permissions = perm


class LocalTokenStore:
    """Global in-memory storage system for access tokens"""

    tokens: dict[str, VerifiedToken] = dict()
    lock = threading.Lock()

    @classmethod
    def add_token(cls, new_token: VerifiedToken) -> None:
        with cls.lock:
            cls.tokens[new_token.token] = new_token

    @classmethod
    def get(cls, other_token: str) -> VerifiedToken | None:
        with cls.lock:
            other_b = other_token.encode("utf-8")
            other_sha_256 = sha256(other_b).hexdigest()
            if verified_tok := cls.tokens.get(other_sha_256):
                if not verified_tok.is_expired():
                    return verified_tok
                else:
                    cls.tokens.pop(verified_tok.token)
                    return
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
    x_dev_permission_level: int = Header(20),
) -> VerifiedToken:
    error = None
    start_ = time.time()
    if verified_token := LocalTokenStore.get(token.credentials):
        if verified_token.permissions == Permissions.developer:
            verified_token.set_simulated_permissions(x_dev_permission_level)
        logger.info(f"Auth(cached): {time.time() - start_}s")
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
                    case TUI.MS_POWER_AUTOMATE.value:
                        user_info = dict(
                            nickname="MS Power Automate",
                            name="MS Power Automate",
                            email="",
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
                if verified_token.permissions == Permissions.developer:
                    verified_token.set_simulated_permissions(x_dev_permission_level)
                LocalTokenStore.add_token(new_token=verified_token)
                logger.info(f"Auth(verified): {time.time() - start_}s")
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
        except ValidationError as e:
            raise e
        except:
            import traceback as tb

            traceback = tb.format_exc()
            logger.critical(traceback)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=traceback)

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

    PRICE_COLUMNS = [
        "zero-discount-price",
        "material-group-discount",
        "material-group-net-price",
        "snp-discount",
        "snp-price",
        "net-price",
        "discount",
        "price",
    ]

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
        # other attributes
        self.filters: dict = kwargs
        self.version: int

    def permitted_primary_resource_ids(
        self, session: Session
    ) -> tuple[Column, set[int]]:

        primary_id_col, queries = self._resource.permitted_primary_resource_ids(
            self.token.email, **self.filters
        )
        get_result = partial(
            self.get_result_from_id_association_queries, session, **queries
        )
        return primary_id_col, (
            get_result(**self.filters) if self.filters else get_result()
        )

    def permitted_customer_location_ids(self, session: Session) -> set[int]:
        queries = permitted_customer_location_ids(
            email=self.token.email, version=self.version
        )
        get_result = partial(
            self.get_result_from_id_association_queries, session, **queries
        )
        return get_result(**self.filters) if self.filters else get_result()

    def get_result_from_id_association_queries(
        self,
        session: Session,
        sql_admin: str,
        sql_manager: str,
        sql_user_only: str,
        sql_sca_employee: str,
        sql_sca_admin: str,
        **filters,
    ) -> set[int]:
        """Run queries provided by SQL Alchemy models that return a set of integer IDs
        used for gating and filtering. Used for both customer locations and object
        association tests"""
        queries_by_user = {
            UserTypes.customer_std: sql_user_only,
            UserTypes.customer_manager: sql_manager,
            UserTypes.customer_admin: sql_admin,
            UserTypes.sca_employee: sql_sca_employee,
            UserTypes.sca_admin: sql_sca_admin,
            # UserTypes.developer: sql_admin,
        }
        if self.token.permissions == Permissions.developer:
            user_type = UserTypes[self.token.sim_permissions.name]
        else:
            user_type = UserTypes[self.token.permissions.name]
        query = queries_by_user[user_type]
        filters_suffixed = {k + "_1": v for k, v in filters.items()}
        result = session.scalars(
            text(query), dict(email_1=self.token.email, **filters_suffixed)
        ).all()
        return set(result) if result else set()

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
        start_ = time.time()
        if self._admin or self._sca:
            result = result_query()
        elif self._customer or self._dev:
            ids = self.permitted_customer_location_ids(session=session)
            if not ids:
                raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
            result = result_query(permitted_ids=ids)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        match result:
            case JSONAPIResponse():
                result = result.data
        if not result["data"]:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
        logger.info(f"Query Time: {time.time()-start_}s")
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
                result = result.data
            case dict():
                result = result
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
                result = result.data
            case dict():
                result = result
        return result

    @standard_error_handler
    def delete(
        self,
        session: Session,
        obj_id: int | str,
        primary_id: Optional[int] = None,
        hard_delete: bool = False,
    ) -> None:
        self.gate(session, primary_id, obj_id)
        if hard_delete:
            self._serializer.delete_resource(
                session=session,
                data={},
                api_type=self._resource.__jsonapi_type_override__,
                obj_id=obj_id,
            )
        else:
            now = datetime.now()
            api_type = self._resource.__jsonapi_type_override__
            # NOTE remember to use kebab case in keys for this custom object
            data = {
                "data": {
                    "id": obj_id,
                    "type": api_type,
                    "attributes": {"deleted-at": now},
                }
            }
            self._serializer.patch_resource(
                session=session,
                json_data=data,
                api_type=api_type,
                obj_id=obj_id,
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)


class CustomersOperations(SecOp):

    def __init__(
        self, token: VerifiedToken, resource: SQLAlchemyModel, prefix: str = ""
    ) -> None:
        super().__init__(token, resource)
        self._primary_resource = SCACustomer
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix=prefix)
        self.version = 1


class AGasOperations(SecOp):
    def __init__(
        self, token: VerifiedToken, resource: SQLAlchemyModel, prefix: str = ""
    ) -> None:
        super().__init__(token, resource)
        self._primary_resource = None
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)
        self.version = 1


class AtcoOperations(SecOp):

    def __init__(
        self, token: VerifiedToken, resource: SQLAlchemyModel, prefix: str = ""
    ) -> None:
        super().__init__(token, resource)
        self._primary_resource = None
        self._associated_resource = resource != self._primary_resource
        self._serializer = serializer_partial(prefix)
        self.version = 1


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
        self.version = 2


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
        self.version = 2


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
        self.version = 2


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
        self.version = 2


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
        self.version = 2


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
        self.version = 2


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
        self.version = 2


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
        self.version = 2


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
        self.version = 2


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
        self.version = 2


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
        self.version = 2
