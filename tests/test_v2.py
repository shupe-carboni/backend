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

ROUTES = [
    VENDORS_PREFIX,
    VENDORS_PREFIX / "TEST_VENDOR",
    VENDORS_PREFIX / "TEST_VENDOR" / "vendors-attrs",
    VENDORS_PREFIX / "TEST_VENDOR" / "relationships" / "vendors-attrs",
    VENDORS_PREFIX / "TEST_VENDOR" / "vendor-products",
    VENDORS_PREFIX / "TEST_VENDOR" / "relationships" / "vendor-products",
    VENDORS_PREFIX / "TEST_VENDOR" / "vendor-product-classes",
    VENDORS_PREFIX / "TEST_VENDOR" / "relationships" / "vendor-product-classes",
    VENDORS_PREFIX / "TEST_VENDOR" / "vendor-pricing-classes",
    VENDORS_PREFIX / "TEST_VENDOR" / "relationships" / "vendor-pricing-classes",
    VENDORS_PREFIX / "TEST_VENDOR" / "vendors-attrs" / "vendor-attrs-changelog",
    VENDORS_PREFIX / "TEST_VENDOR" / "vendor-products" / "vendor-product-attrs",
    VENDORS_PREFIX / "TEST_VENDOR" / "vendor-customers" / "vendor-pricing-by-customer",
    VENDORS_PREFIX
    / "TEST_VENDOR"
    / "vendor-customers"
    / "vendor-product-class-discounts",
    VENDORS_PREFIX
    / "TEST_VENDOR"
    / "vendor-customers"
    / "vendor-customer-pricing-classes",
    VENDORS_PREFIX / "TEST_VENDOR" / "vendor-customers" / "vendor-quotes",
]
ROUTE_PERM_RESP_ALL_ALLOWED = [
    (str(route), perm, resp) for route in ROUTES for perm, resp in ALL_ALLOWED
]


@mark.parametrize("route,perm,response_code", ROUTE_PERM_RESP_ALL_ALLOWED)
def test_vendors_collection(route, perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(route)
    assert resp.status_code == response_code or resp.status_code == 204, pprint(
        resp.content
    )
