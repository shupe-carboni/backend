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
