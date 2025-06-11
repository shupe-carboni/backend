from fastapi.testclient import TestClient
from fastapi import Header
from pytest import mark
from pprint import pformat

from app.main import app
from app.auth import authenticate_auth0_token
from tests import auth_overrides

test_client = TestClient(app)

EXPECTED_CUSTOMERS_PER_SIM = [
    (13, {}),
    (12, {55, 255, 256}),
    (11, {55, 255}),
    (10, {55}),
    (9, {}),
]


def auth_with_custom_header_for_dev(x_dev_permission_level: int = Header()):
    return auth_overrides.DeveloperToken(x_dev_permission_level)


@mark.parametrize("sim_perm,ids", EXPECTED_CUSTOMERS_PER_SIM)
def test_dev_simulated_perms(sim_perm: int, ids: set[int]):
    """Test whether simulated permissions settings are applying
    different querys, resulting in changes to vendor-customer filtering"""
    app.dependency_overrides[authenticate_auth0_token] = auth_with_custom_header_for_dev
    route = "/v2/vendors/adp/vendor-customers"
    resp = test_client.get(route, headers={"X-Dev-Permission-Level": str(sim_perm)})
    if not ids:
        error_resp: dict = resp.json()["detail"]
        assert resp.status_code == 400
        assert "simulated_permissions" in error_resp.keys()
        assert set(("range", "defined")) == set(
            error_resp["simulated_permissions"].keys()
        )
    else:
        returned_ids = set([customer["id"] for customer in resp.json()["data"]])
        assert returned_ids == ids, pformat(resp.text)
