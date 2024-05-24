from fastapi.testclient import TestClient
from app.main import app
from app.auth import authenticate_auth0_token
from tests import auth_overrides
from pytest import mark
from random import randint
from datetime import datetime, timedelta

test_client = TestClient(app)

ADP_TEST_CUSTOMER_ID = 59

PATH_PREFIX = "/adp/adp-quotes"

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


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_quotes_collection(perm, response_code):
    url = PATH_PREFIX
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_quote_resource(perm, response_code):
    url = PATH_PREFIX
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url + "/1")
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", SCA_ONLY)
def test_new_quote(perm, response_code):
    url = PATH_PREFIX
    QN = randint(1000, 9999)
    app.dependency_overrides[authenticate_auth0_token] = perm
    new_quote = {
        "adp_customer_id": ADP_TEST_CUSTOMER_ID,
        "adp_quote_id": f"QN-{QN}",
        "job_name": "Test Job",
        "expires_at": (datetime.today().date() + timedelta(days=90)),
        "status": "proposed",
        "place_id": 4644585,
        "customer_location_id": 5,
    }
    resp = test_client.post(url, data=new_quote)
    assert resp.status_code == response_code, resp.text
