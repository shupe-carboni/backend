from pytest import mark
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.db import Stage
from app.auth import authenticate_auth0_token
from app.db import S3 as real_S3
from tests import auth_overrides
from datetime import datetime, timedelta
import pandas as pd
from pprint import pprint
from random import randint

# pytest doesn't like putting this under TYPE_CHECKING
from app.auth import VerifiedToken

test_client = TestClient(app)

TEST_CUSTOMER_ID = 50
TEST_PRICE_LEVEL_ID = 38
TEST_PRICING_ID = 1
TEST_PRICE_SPECIAL_ID = 1856
TEST_PRODUCT_ID = 1

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

SCA_ONLY_INCLUDING_DEV = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [200, 200, 401, 401, 401, 200],
    )
)

SCA_ONLY_EXCLUDING_DEV = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [200, 200, 401, 401, 401, 401],
    )
)

COLLECTION_FILTERING = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [7, 7, 2, 2, 1, 2],
        [
            {28, 20, 50, 51, 7, 49, 47},
            {28, 20, 50, 51, 7, 49, 47},
            {50, 51},
            {50, 51},
            {50},
            {50, 51},
        ],
    )
)

resources = [
    "friedrich-customers",
    "friedrich-products",
    "friedrich-pricing",
    "friedrich-pricing-special",
    "friedrich-customer-price-levels",
]


related_by_resource = {
    "friedrich-customers": [
        f"{TEST_CUSTOMER_ID}/customers",
        f"{TEST_CUSTOMER_ID}/friedrich-pricing-special",
        f"{TEST_CUSTOMER_ID}/friedrich-customer-price-levels",
        f"{TEST_CUSTOMER_ID}/relationships/customers",
        f"{TEST_CUSTOMER_ID}/relationships/friedrich-pricing-special",
        f"{TEST_CUSTOMER_ID}/relationships/friedrich-customer-price-levels",
    ],
    "friedrich-products": [
        f"{TEST_PRODUCT_ID}/friedrich-pricing",
        f"{TEST_PRODUCT_ID}/friedrich-pricing-special",
        f"{TEST_PRODUCT_ID}/relationships/friedrich-pricing",
        f"{TEST_PRODUCT_ID}/relationships/friedrich-pricing-special",
    ],
    "friedrich-pricing": [
        f"{TEST_PRICING_ID}/friedrich-products",
        f"{TEST_PRICING_ID}/relationships/friedrich-products",
    ],
    "friedrich-pricing-special": [
        f"{TEST_PRICE_SPECIAL_ID}/friedrich-customers",
        f"{TEST_PRICE_SPECIAL_ID}/friedrich-products",
        f"{TEST_PRICE_SPECIAL_ID}/relationships/friedrich-customers",
        f"{TEST_PRICE_SPECIAL_ID}/relationships/friedrich-products",
    ],
    "friedrich-customer-price-levels": [
        f"{TEST_PRICE_LEVEL_ID}/friedrich-customers",
        f"{TEST_PRICE_LEVEL_ID}/relationships/friedrich-customers",
    ],
}

resources += [
    f"{primary}/{secondary}"
    for primary, routes in related_by_resource.items()
    for secondary in routes
]
GET_PATHS = [
    (*perm_and_code, path) for path in resources for perm_and_code in ALL_ALLOWED
]


@mark.parametrize("perm,count,ids", COLLECTION_FILTERING)
def test_collection_filtering(perm, count, ids):
    """takes awhile due to the number of objects getting returned
    unlike the adp version, this query is testing the chaining together
    of includes. Prior to a fix in an override of _render_full_resource,
    this query would have returned special pricing and associated customers
    not associated with the dev customer account.

    The issue is with an intermediate linking table, products, that maps
    friedrich-pricing to products, which also maps to special customer pricing.
    """
    potentially_filter_defeating_req = (
        "/vendors/friedrich/friedrich-pricing"
        "?include=friedrich-products.friedrich-pricing-special.friedrich-customers"
        "&fields[friedrich-pricing]=id"
    )
    app.dependency_overrides[authenticate_auth0_token] = perm
    response = test_client.get(potentially_filter_defeating_req)
    customer_ids_in_included = set(
        [
            x["id"]
            for x in response.json()["included"]
            if x["type"] == "friedrich-customers"
        ]
    )
    assert len(customer_ids_in_included) == count
    assert customer_ids_in_included == ids


@mark.parametrize("perm,response_code,path", GET_PATHS)
def test_gets(perm, response_code, path):
    app.dependency_overrides[authenticate_auth0_token] = perm
    response = test_client.get("/vendors/friedrich/" + path)
    assert response.status_code == response_code
