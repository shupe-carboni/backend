from fastapi.testclient import TestClient
from app.main import app
from app.auth import authenticate_auth0_token
from tests import auth_overrides
from pytest import mark
from pprint import pformat
from httpx import Response
from app.jsonapi.sqla_models import *
from pathlib import Path
from random import random
from pydantic import BaseModel

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

ALL_PERMS: list[auth_overrides.Token] = [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM]

TEST_VENDOR_CUSTOMER_1_ID = 169
TEST_VENDOR_CUSTOMER_2_ID = 176
TEST_VENDOR_CUSTOMER_3_ID = 177
MANAGER_CUSTOMER_IDS = [TEST_VENDOR_CUSTOMER_1_ID, TEST_VENDOR_CUSTOMER_2_ID]
ADMIN_CUSTOMER_IDS = [
    TEST_VENDOR_CUSTOMER_1_ID,
    TEST_VENDOR_CUSTOMER_2_ID,
    TEST_VENDOR_CUSTOMER_3_ID,
]

NOT_IMPLEMENTED = list(zip(ALL_PERMS, [501] * len(ALL_PERMS)))
ALL_ALLOWED = list(
    zip(
        ALL_PERMS,
        [200] * (len(SCA_PERMS) + len(CUSTOMER_PERMS) + 1),
    )
)

SCA_ONLY = list(
    zip(
        ALL_PERMS,
        [200, 200, 401, 401, 401, 200],
    )
)

EXCLUDE_BASE_CUSTOMER = list(
    zip(
        ALL_PERMS,
        [200, 200, 200, 200, 401, 200],
    )
)
VENDOR_CUSTOMER_IDS_BY_PERM = list(
    zip(
        ALL_PERMS,
        [
            ADMIN_CUSTOMER_IDS,
            ADMIN_CUSTOMER_IDS,
            ADMIN_CUSTOMER_IDS,
            MANAGER_CUSTOMER_IDS,
            [TEST_VENDOR_CUSTOMER_1_ID],
            ADMIN_CUSTOMER_IDS,
        ],
    )
)

VENDORS_PREFIX = Path(f"/v2/{VENDOR_RESOURCE}")
TEST_VENDOR = VENDORS_PREFIX / "TEST_VENDOR"
TEST_VENDOR_ATTR = str(4)
TEST_VENDOR_PRODUCT = str(2355)
TEST_VENDOR_TEST_CUSTOMER = (
    TEST_VENDOR / "vendor-customers" / str(TEST_VENDOR_CUSTOMER_1_ID)
)

ALL_ROUTES = [
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
    TEST_VENDOR / "vendor-customers",
    TEST_VENDOR / "relationships" / "vendor-customers",
    # chained static collections
    TEST_VENDOR / "vendors-attrs" / "vendors-attrs-changelog",
    TEST_VENDOR / "vendor-products" / "vendor-product-attrs",
    TEST_VENDOR / "vendor-customers" / "vendor-pricing-by-customer",
    TEST_VENDOR / "vendor-customers" / "vendor-product-class-discounts",
    TEST_VENDOR / "vendor-customers" / "vendor-customer-pricing-classes",
    TEST_VENDOR / "vendor-customers" / "vendor-quotes",
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
]
ROUTE_PERM_RESP_ALL_ALLOWED = [
    (str(route), perm, resp) for route in ALL_ROUTES for perm, resp in ALL_ALLOWED
]
CUSTOMER_SENSITIVE_COLLECTION_ROUTES = [
    TEST_VENDOR / "vendor-customers",
    TEST_VENDOR / "vendor-customers" / "vendor-pricing-by-customer",
    TEST_VENDOR / "vendor-customers" / "vendor-product-class-discounts",
    TEST_VENDOR / "vendor-customers" / "vendor-customer-pricing-classes",
    TEST_VENDOR / "vendor-customers" / "vendor-quotes",
]
ROUTE_FILTERING = [
    (str(route) + "?page_number=0", perm, ids)
    for route in CUSTOMER_SENSITIVE_COLLECTION_ROUTES
    for perm, ids in VENDOR_CUSTOMER_IDS_BY_PERM
]


@mark.parametrize("route,perm,response_code", ROUTE_PERM_RESP_ALL_ALLOWED)
def test_vendor_endpoint_response_codes(
    route: str, perm: auth_overrides.Token, response_code: int
):
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(route)
    no_content = resp.status_code == 204
    expected_code = resp.status_code == response_code
    internal_error = resp.status_code == 500
    assert expected_code or no_content, pformat(
        resp.text if internal_error else resp.json()
    )
    if expected_code and response_code == 200:
        resource = route.split("/")[-1]
        if "-" in resource:
            types_in_resp = set([record["type"] for record in resp.json()["data"]])
            assert len(types_in_resp) == 1 and types_in_resp.pop() == resource


@mark.parametrize("route,perm,ids", ROUTE_FILTERING)
def test_vendor_endpoint_response_content(
    route: str, perm: auth_overrides.Token, ids: list[int]
):
    """Return data ought to be filtered as expected based on the vendor in the path
    as well as the permission type"""
    app.dependency_overrides[authenticate_auth0_token] = perm
    if route.split("/")[-1] != "vendor-customers?page_number=0":
        route += "&include=vendor-customers"
        resp = test_client.get(route)
        returned_ids = sorted([customer["id"] for customer in resp.json()["included"]])
        assert returned_ids == ids
    else:
        resp = test_client.get(route)
        assert resp.status_code < 500, pformat(resp.text)
        returned_ids = sorted([customer["id"] for customer in resp.json()["data"]])
        match perm:
            case auth_overrides.AdminToken | auth_overrides.SCAEmployeeToken:
                assert set(returned_ids) >= set(ids) and len(returned_ids) > len(ids)
            case _:
                assert returned_ids == ids


post_patch_delete_outline = [
    {
        "route": VENDORS_PREFIX,
        "status_codes": NOT_IMPLEMENTED,
        "post": {
            "data": {
                "attributes": {"name": f"TEST VENDOR {int((random()+1) * 1000000000)}"}
            },
        },
    },
    {
        "route": TEST_VENDOR,
        "status_codes": SCA_ONLY,
        "patch": {
            "data": {
                "id": "TEST_VENDOR",
                "attributes": {"headquarters": f"{int((random()+1) * 1000000000)}"},
            },
        },
    },
]

POST_PATCH_DELETE_PARAMS: list[tuple] = []
for route in post_patch_delete_outline:
    post = route.get("post")
    patch = route.get("patch")
    if post:
        for status_code in route["status_codes"]:
            perm, sc = status_code
            new_item = (perm, sc, "post", str(route["route"]), post)
            POST_PATCH_DELETE_PARAMS.append(new_item)
    if patch:
        for status_code in route["status_codes"]:
            perm, sc = status_code
            new_item = (perm, sc, "patch", str(route["route"]), patch)
            POST_PATCH_DELETE_PARAMS.append(new_item)


@mark.parametrize("perm,status_code,method,route,data", POST_PATCH_DELETE_PARAMS)
def test_post_patch_delete(perm, status_code, method, route, data):
    """
    post new, change it if it can be changed, and delete it (soft or hard)
    by route -> each needs it's own object structure, some may need to capture the id
    returned and use it in order dependent operations (i.e. product needs to be created
    before a product attribute.) -> if it can be modified, provide an object for patch
    request, and if it's not modifiable, skip this step -> delete the objects, order
    doesn't matter for soft deletes (patches to 'deleted-at' under the hood) but do them
    in reverse order.

    Patches and deletes shall be called only on objects created by POST requests within
    this test, albeit most records created will remain in the test DB soft-deleted.

    Assert expected status codes by token type
        post - 200/401/501
        patch - 200/401/501
        delete - 204/401/501
    """
    app.dependency_overrides[authenticate_auth0_token] = perm
    client_method = getattr(test_client, method)
    resp: Response = client_method(route, json=data)
    assert resp.status_code == status_code, pformat(resp.text)
