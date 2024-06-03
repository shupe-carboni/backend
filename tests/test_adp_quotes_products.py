from fastapi.testclient import TestClient
from app.main import app
from app.auth import authenticate_auth0_token
from tests import auth_overrides
from pytest import mark
from app.jsonapi.sqla_models import ADPQuoteProduct

test_client = TestClient(app)

ADP_TEST_CUSTOMER_ID = 59
TEST_CUSTOMER_LOCATION = 5
TEST_CUSTOMER_PLACE = 4644585

PATH_PREFIX = f"/adp/{ADPQuoteProduct.__jsonapi_type_override__}"

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

NONE_ALLOWED = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [401, 401, 401, 401, 401, 401],
    )
)

NOT_IMPLEMENTED = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [501, 501, 501, 501, 501, 501],
    )
)


@mark.parametrize("perm,response_code", NOT_IMPLEMENTED)
def test_quote_products_collection(perm, response_code):
    url = PATH_PREFIX
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", NOT_IMPLEMENTED)
def test_quote_products_resource(perm, response_code):
    url = PATH_PREFIX + "/1"
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code
