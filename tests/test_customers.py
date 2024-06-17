from pytest import mark
from pathlib import Path
from app.main import app
from fastapi.testclient import TestClient
from app.customers.models import NewCMMSSNSCustomer, ModCustomer
from app.auth import authenticate_auth0_token
from app.customers.customers import get_new_cmmssns_customer_method
from tests import auth_overrides
from random import randint
from pprint import pprint


test_client = TestClient(app)
CUSTOMER_ID = 999999  # NOTE associated with TEST CUSTOMER

app.dependency_overrides[get_new_cmmssns_customer_method] = (
    auth_overrides.mock_get_mock_new_cmmssns_customer
)

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

SCA_ADMIN_ONLY = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [200, 401, 401, 401, 401, 401],
    )
)


SCA_DEV_AND_CUSTOMER_ADMIN_ONLY = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [200, 200, 200, 401, 401, 200],
    )
)

BASE_GETS = ["/customers", f"/customers/{CUSTOMER_ID}"]
RELATED_GETS = [
    BASE_GETS[-1] + f"/{related}"
    for related in ["customer-locations", "adp-customers", "adp-customer-terms"]
]
RELATIONSHIP_GETS = [
    BASE_GETS[-1] + f"/relationships/{related}"
    for related in ["customer-locations", "adp-customers", "adp-customer-terms"]
]
GET_PATHS = [
    (*perm_and_code, path)
    for path in BASE_GETS + RELATED_GETS + RELATIONSHIP_GETS
    for perm_and_code in SCA_DEV_AND_CUSTOMER_ADMIN_ONLY
]


@mark.parametrize("perm,response_code", SCA_ADMIN_ONLY)
def test_new_customer_and_delete(perm, response_code):
    ROUTE = Path("/customers")
    app.dependency_overrides[authenticate_auth0_token] = perm
    payload = NewCMMSSNSCustomer(
        data={
            "type": "customers",
            "attributes": {"name": f"TEST {randint(1000, 9999)}"},
        }
    ).model_dump()
    response = test_client.post(str(ROUTE), json=payload)
    assert response.status_code == response_code, pprint(response.json())
    if response_code != 200:
        return
    del_route = ROUTE / str(response.json()["data"]["id"])
    response = test_client.delete(str(del_route))
    assert response.status_code == 204, pprint(response.json())


@mark.parametrize("perm,response_code", SCA_ONLY_EXCLUDING_DEV)
def test_modify_customer(perm, response_code):
    ROUTE = Path("/customers") / str(CUSTOMER_ID)
    app.dependency_overrides[authenticate_auth0_token] = perm
    payload = ModCustomer(
        data={
            "id": CUSTOMER_ID,
            "type": "customers",
            "attributes": {
                # "name": "TEST CUSTOMER",
                # "logo": "customers/999999/logo/py-color.jpg",
                "domains": ["somedomain.com", "someotherdomain.net"],
                "buying-group": "AD",
            },
        }
    ).model_dump(exclude_none=True, by_alias=True)
    response = test_client.patch(str(ROUTE), json=payload)
    assert response.status_code == response_code, pprint(response.json())
    if response.status_code == 200:
        assert response.json()["data"]["attributes"].get("name") is not None


@mark.parametrize("perm,response_code,path", GET_PATHS)
def test_customer_gets(perm, response_code, path):
    app.dependency_overrides[authenticate_auth0_token] = perm
    response = test_client.get(path)
    assert response.status_code == response_code
