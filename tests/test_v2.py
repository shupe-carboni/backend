from fastapi.testclient import TestClient
from app.main import app
from app.auth import authenticate_auth0_token
from tests import auth_overrides
from pytest import mark
from random import randint, choice
from pprint import pprint
from app.jsonapi.sqla_models import *
from pathlib import Path

test_client = TestClient(app)

VENDOR_RESOURCE = Vendor.__jsonapi_type_override__
VENDORS_PREFIX = Path(f"/{VENDOR_RESOURCE}")
INFO_RESOURCE = SCAVendorInfo.__jsonapi_type_override__
INFO_PREFIX = VENDORS_PREFIX / INFO_RESOURCE

SCA_PERMS = (
    auth_overrides.AdminToken,
    auth_overrides.SCAEmployeeToken,
)
CUSTOMER_PERMS = (
    auth_overrides.CustomerAdminToken,
    auth_overrides.CustomerManagerToken,
    auth_overrides.CustomerStandardToken,
)
DEV_PERM = auth_overrides.DeveloperToken

ALL_ALLOWED = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [200] * (len(SCA_PERMS) + len(CUSTOMER_PERMS) + 1),
    )
)

SCA_ONLY = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [200, 200, 401, 401, 401, 200],
    )
)

EXCLUDE_BASE_CUSTOMER = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [200, 200, 200, 200, 401, 200],
    )
)


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_vendors_collection(perm, response_code):
    url = str(VENDORS_PREFIX)
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())
