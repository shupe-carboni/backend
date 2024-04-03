import os
import time
import requests
import bcrypt
from enum import Enum, IntEnum
from hashlib import sha256
from dotenv import load_dotenv; load_dotenv()
from pydantic import BaseModel, field_validator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from jose.jwt import get_unverified_header, decode

from typing import Optional
from functools import partial
from sqlalchemy_jsonapi.errors import ResourceNotFoundError
from sqlalchemy_jsonapi.serializer import JSONAPIResponse
from app.db.db import Session, Database
from app.jsonapi.sqla_models import serializer

token_auth_scheme = HTTPBearer()
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
ALGORITHMS = os.getenv('ALGORITHMS')
AUDIENCE = os.getenv('AUDIENCE')
SCA_CLOUD_TUI = os.getenv('SCA_CLOUD_TUI_CLIENT_ID')

status_codes = {
    400: status.HTTP_400_BAD_REQUEST,
    401: status.HTTP_401_UNAUTHORIZED
}

class QuotePermPriority(IntEnum):
    view_only = 1
    customer_std = 10
    customer_manager = 11
    customer_admin = 12
    sca_employee = 20
    sca_admin = 21

class ADPPermPriority(IntEnum):
    view_only = 1
    customer_std = 10
    customer_manager = 11
    customer_admin = 12
    sca_employee = 20
    sca_admin = 21

class VendorPermPriority(IntEnum):
    view_only = 1
    customer_std = 10
    customer_manager = 11
    customer_admin = 12
    sca_employee = 20
    sca_admin = 21

class CustomersPermPriority(IntEnum):
    view_only = 1
    customer_std = 0
    customer_manager = 0
    customer_admin = 0
    sca_employee = 20
    sca_admin = 21

class Permissions(Enum):
    adp = ADPPermPriority
    quotes = QuotePermPriority
    vendors = VendorPermPriority
    customers = CustomersPermPriority

class VerifiedToken(BaseModel):
    """
        Representing a verified token by the hash of the token itself
        along with expiry time and permissions in order to check
        whether or not token should be used and how it can be used.

        This will representation will be used in an in-memory storage system 
        called LocalTokenStore, which will keep a set of VerifiedTokens and check
        for the incoming token in the collection.
    """
    token: bytes
    exp: int
    permissions: dict[str,IntEnum]
    nickname: str
    name: str
    email: str
    email_verified: bool

    def is_expired(self) -> bool:
        return time.time() > self.exp

    @field_validator('token', mode='before')
    def hash_token(cls, value: str):
        token_b = value.encode('utf-8')
        token_256_hash = sha256(token_b).digest()
        salt = bcrypt.gensalt(12)
        return bcrypt.hashpw(token_256_hash, salt)

    def __hash__(self) -> int:
        return self.token.__hash__()

    def is_same_token(self, other: str) -> bool:
        other_b = other.encode('utf-8')
        other_sha_256 = sha256(other_b).digest()
        return bcrypt.checkpw(other_sha_256, self.token)

    def perm_level(self, resource) -> bool:
        if perm := self.permissions.get(resource, None):
            return perm.value
        else:
            return -1


class LocalTokenStore:
    """Global in-memory storage system for access tokens"""
    tokens: set[VerifiedToken] = set()
    @classmethod
    def add_token(cls, new_token: VerifiedToken) -> None:
        cls.tokens.add(new_token)
    @classmethod
    def contains(cls, token: str) -> VerifiedToken|None:
        for verified_token in cls.tokens:
            if verified_token.is_same_token(token):
                if not verified_token.is_expired():
                    return verified_token
        return

def get_user_info(access_token: str) -> dict:
    user_info_ep = AUTH0_DOMAIN + '/userinfo'
    auth_header = {'Authorization': f"Bearer {access_token}"}
    user_info = requests.get(user_info_ep, headers=auth_header)
    if 299 >= user_info.status_code >= 200:
        user_info = user_info.json()
    else:
        raise HTTPException(status_code=status_codes[401], detail="user could not be verified")
    match user_info:
        case {"nickname": a, "name": b, "email": c, "email_verified": d, **other}:
            return {"nickname": a, "name": b, "email": c, "email_verified": d}
        case _:
            raise HTTPException(status_code=status_codes[401], detail="user could not be verified")
        
def set_permissions(all_permissions: list[str]) -> dict[str,Enum]:
    if not all_permissions:
        return dict()
    all_permissions_dict = dict()
    for perm in all_permissions:
        resource, permission = perm.split(':')
        permission = permission.replace('-','_')
        resource_perms = Permissions[resource].value
        try:
            current_perm_lvl = resource_perms[permission] 
        except KeyError:
            current_perm_lvl = 0
        if resource in all_permissions_dict:
            # set the permissions to the most restictive (lowest priority enum value)
            # if more than one permission value is provided for a resource
            if all_permissions_dict[resource] < current_perm_lvl:
                continue
        all_permissions_dict[resource] = current_perm_lvl
    return all_permissions_dict

def find_duplicates(input_list):
    seen = set()
    duplicates = set()
    for item in input_list:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return duplicates

async def authenticate_auth0_token(token: HTTPAuthorizationCredentials=Depends(token_auth_scheme)):
    error = None
    if verified_token := LocalTokenStore.contains(token.credentials):
        return verified_token
    jwks = requests.get(AUTH0_DOMAIN+"/.well-known/jwks.json").json()
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
                    "e": key["e"]             
                }
        if rsa_key:
            try:
                payload = decode(
                    token.credentials,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=AUDIENCE
                )
            except Exception as err:
                error = err
            else:
                permissions = set_permissions(payload['permissions'])
                if payload['azp'] == SCA_CLOUD_TUI:
                    verified_token = VerifiedToken(
                        token=token.credentials,
                        exp=payload['exp'],
                        permissions=permissions,
                        nickname='SCA Cloud TUI',
                        name='SCA Cloud TUI',
                        email='',
                        email_verified=True,
                    )
                else:
                    verified_token = VerifiedToken(
                        token=token.credentials,
                        exp=payload['exp'],
                        permissions=permissions,
                        **get_user_info(token.credentials)
                    )
                LocalTokenStore.add_token(new_token=verified_token)
                return verified_token
        else:
            error = "No RSA key found in JWT Header"
    raise HTTPException(status_code=status_codes[401], detail=str(error)) 


def perm_category_present(token: VerifiedToken, category: str) -> VerifiedToken:
    perm_level = token.perm_level(category)
    if not perm_level:
        raise HTTPException(
            status_code=status_codes[401],
            detail=f'Permissions for access to {category.title()} have not been defined.'
        )
    elif perm_level <= 0:
        raise HTTPException(
            status_code=status_codes[401],
            detail=f'Access to {category.title()} is restricted.'
        )
    return token

def adp_perms_present(token: VerifiedToken = Depends(authenticate_auth0_token)) -> VerifiedToken:
    return perm_category_present(token, 'adp')

def vendor_perms_present(token: VerifiedToken = Depends(authenticate_auth0_token)) -> VerifiedToken:
    return perm_category_present(token, 'vendors')

def quotes_perms_present(token: VerifiedToken = Depends(authenticate_auth0_token)) -> VerifiedToken:
    return perm_category_present(token, 'quotes')

def customers_perms_present(token: VerifiedToken = Depends(authenticate_auth0_token)) -> VerifiedToken:
    return perm_category_present(token, 'customers')

def adp_quotes_perms(token: VerifiedToken = Depends(authenticate_auth0_token)) -> VerifiedToken:
    perm_category_present(token, 'adp')
    perm_category_present(token, 'qutoes')
    return token

class UnverifiedEmail(Exception): ...

def standard_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UnverifiedEmail:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Email not verified")
        except ResourceNotFoundError:
            raise HTTPException(status.HTTP_204_NO_CONTENT)
        except:
            import traceback as tb
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=tb.format_exc())
    return wrapper

@standard_error_handler
def secured_get_query(
        db: Database,
        session: Session,
        token: VerifiedToken,
        auth_scheme: Permissions,
        resource: str,
        query: dict,
        obj_id: Optional[int] = None,
        relationship: bool = False,
        related_resource: str = None
    ):
    if not token.email_verified:
        raise UnverifiedEmail
    perm_lookup_name: str = auth_scheme.name
    the_perm: IntEnum = token.permissions.get(perm_lookup_name)
    arguments = (obj_id, relationship, related_resource)
    match arguments:
        case None, False, None:
            result_query = partial(
                serializer.get_collection,
                session=session,
                query=query,
                api_type=resource,
                )
        case int(), False, None:
            result_query = partial(
                serializer.get_resource,
                session=session,
                query=query,
                api_type=resource,
                obj_id=obj_id,
                obj_only=True
            )
        case int(), False, str():
            result_query = partial(
                serializer.get_related,
                session=session,
                query=query,
                api_type=resource,
                obj_id=obj_id,
                rel_key=related_resource
            )
        case int(), True, str():
            result_query = partial(
                serializer.get_relationship,
                session=session,
                query=query,
                api_type=resource,
                obj_id=obj_id,
                rel_key=related_resource
            )
        case _:
            raise Exception('Invalid argument set supplied to auth.secured_get_query')
    if the_perm >= auth_scheme.value.sca_employee:
        result = result_query()
    elif the_perm >= auth_scheme.value.customer_std:
        ids = db.get_permitted_customer_location_ids(
            session=session,
            email_address=token.email,
            select_type=the_perm.name
        )
        result = result_query(permitted_ids=ids)
    match result:
        case JSONAPIResponse():
            return result.data
        case _:
            return result
