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
VENDORS_PREFIX = Path(f"/{VENDOR_RESOURCE}")
TEST_VENDOR = VENDORS_PREFIX / "TEST_VENDOR"
TEST_VENDOR_ATTR = str(4)
TEST_VENDOR_PRODUCT = str(2355)
TEST_VENDOR_TEST_CUSTOMER = TEST_VENDOR / "vendor-customers" / str(169)

ROUTES = [
    VENDORS_PREFIX,
    TEST_VENDOR,
    TEST_VENDOR / "vendors-attrs",
    TEST_VENDOR / "relationships" / "vendors-attrs",
    TEST_VENDOR / "vendor-products",
    TEST_VENDOR / "relationships" / "vendor-products",
    TEST_VENDOR / "vendor-product-classes",
    TEST_VENDOR / "relationships" / "vendor-product-classes",
    TEST_VENDOR / "vendor-pricing-classes",
    TEST_VENDOR / "relationships" / "vendor-pricing-classes",
    # chained static collections
    TEST_VENDOR / "vendors-attrs" / "vendors-attrs-changelog",
    TEST_VENDOR / "vendor-products" / "vendor-product-attrs",
    TEST_VENDOR / "vendor-customers" / "vendor-pricing-by-customer",
    TEST_VENDOR / "vendor-customers" / "vendor-product-class-discounts",
    TEST_VENDOR / "vendor-customers" / "vendor-customer-pricing-classes",
    TEST_VENDOR / "vendor-customers" / "vendor-quotes",
    # TODO
    TEST_VENDOR / "vendor-customers" / "customer-pricing-by-class",
    TEST_VENDOR / "vendor-customers" / "customer-pricing-by-customer",
    # chained dynamic resource/collections by object
    TEST_VENDOR / "vendors-attrs" / TEST_VENDOR_ATTR,
    TEST_VENDOR / "vendors-attrs" / TEST_VENDOR_ATTR / "vendors-attrs-changelog",
    TEST_VENDOR / "vendor-products" / TEST_VENDOR_PRODUCT,
    TEST_VENDOR / "vendor-products" / TEST_VENDOR_PRODUCT / "vendor-product-attrs",
    TEST_VENDOR_TEST_CUSTOMER,
    TEST_VENDOR_TEST_CUSTOMER / "vendor-pricing-by-customer",
    TEST_VENDOR_TEST_CUSTOMER / "vendor-product-class-discounts",
    TEST_VENDOR_TEST_CUSTOMER / "vendor-customer-pricing-classes",
    TEST_VENDOR_TEST_CUSTOMER / "vendor-quotes",
    # TODO
    TEST_VENDOR_TEST_CUSTOMER / "customer-pricing-by-class",
    TEST_VENDOR_TEST_CUSTOMER / "customer-pricing-by-customer",
]
ROUTE_PERM_RESP_ALL_ALLOWED = [
    (str(route), perm, resp) for route in ROUTES for perm, resp in ALL_ALLOWED
]


@mark.parametrize("route,perm,response_code", ROUTE_PERM_RESP_ALL_ALLOWED)
def test_vendor_response_codes(route, perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(route)
    valid_code = resp.status_code == response_code or resp.status_code == 204
    internal_error = resp.status_code == 500
    assert valid_code, pprint(resp.text if internal_error else resp.json())
