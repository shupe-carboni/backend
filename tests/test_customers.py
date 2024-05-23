from fastapi.testclient import TestClient
from app.main import app
from app.customers.models import CustomerResponse, NewCMMSSNSCustomer, ModCustomer
from app.customers.locations.models import (
    RelatedLocationResponse,
    LocationRelationshipsResponse,
)
from app.adp.models import (
    RelatedCustomerResponse,
    CustomersRelResp,
    RelatedADPCustomerTermsResp,
    ADPCustomerTermsRelationshipsResp,
)
from app.auth import authenticate_auth0_token
from app.customers.customers import get_new_cmmssns_customer_method
from tests import auth_overrides
from random import randint

test_client = TestClient(app)
CUSTOMER_ID = 999999  # NOTE associated with TEST CUSTOMER

app.dependency_overrides[get_new_cmmssns_customer_method] = (
    auth_overrides.mock_get_mock_new_cmmssns_customer
)


def test_new_customer():
    ROUTE = "/customers"
    method = test_client.post
    perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
        auth_overrides.DeveloperToken,
    )
    response_codes = (200, 200, 401, 401, 401, 401)
    assert len(perms) == len(response_codes)
    for perm, rc in zip(perms, response_codes):
        app.dependency_overrides[authenticate_auth0_token] = perm
        payload = NewCMMSSNSCustomer(
            data={
                "type": "customers",
                "attributes": {"name": f"TEST {randint(1000, 9999)}"},
            }
        ).model_dump()
        response = method(ROUTE, json=payload)
        assert response.status_code == rc
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_modify_customer():
    ROUTE = f"/customers/{CUSTOMER_ID}"
    method = test_client.patch
    perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
        auth_overrides.DeveloperToken,
    )
    response_codes = (200, 200, 401, 401, 401, 401)
    assert len(perms) == len(response_codes)
    for perm, rc in zip(perms, response_codes):
        app.dependency_overrides[authenticate_auth0_token] = perm
        payload = ModCustomer(
            data={
                "id": CUSTOMER_ID,
                "type": "customers",
                "attributes": {
                    "name": "TEST CUSTOMER",
                    "logo": "customers/999999/logo/py-color.jpg",
                    "domains": ["somedomain.com", "someotherdomain.net"],
                    "buying_group": "AD",
                },
            }
        ).model_dump()
        response = method(ROUTE, json=payload)
        assert response.status_code == rc, f"{response.status_code}: {perm}"
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_collection():
    ROUTE = "/customers"
    method = test_client.get

    perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
        auth_overrides.DeveloperToken,
    )
    response_codes = (200, 200, 401, 401, 401, 401)

    data_lens = (None, None, 1, 1, 1, 1)
    assert len(perms) == len(response_codes) == len(data_lens)
    for perm, rc, dl in zip(perms, response_codes, data_lens):
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = method(ROUTE)
        assert response.status_code == rc
        if rc == 200:
            assert CustomerResponse(**response.json())
            if dl:
                assert len(response.json()["data"]) == dl
            else:
                assert len(response.json()["data"]) > 1
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_resource():
    ROUTE = f"/customers/{CUSTOMER_ID}"
    method = test_client.get
    perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
        auth_overrides.DeveloperToken,
    )
    response_codes = (200, 200, 401, 401, 401, 401)
    assert len(perms) == len(response_codes)
    for perm, rc in zip(perms, response_codes):
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = method(ROUTE)
        assert response.status_code == rc
        if rc == 200:
            assert CustomerResponse(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_customer_locations():
    ROUTE = f"/customers/{CUSTOMER_ID}/customer-locations"
    method = test_client.get
    perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
        auth_overrides.DeveloperToken,
    )
    response_codes = (200, 200, 401, 401, 401, 200)
    assert len(perms) == len(response_codes)
    for perm, rc in zip(perms, response_codes):
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = method(ROUTE)
        assert response.status_code == rc
        if rc == 200:
            assert RelatedLocationResponse(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_customer_locations():
    ROUTE = f"/customers/{CUSTOMER_ID}/relationships/customer-locations"
    method = test_client.get
    perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
        auth_overrides.DeveloperToken,
    )
    response_codes = (200, 200, 401, 401, 401, 200)
    assert len(perms) == len(response_codes)
    for perm, rc in zip(perms, response_codes):
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = method(ROUTE)
        assert response.status_code == rc
        if rc == 200:
            assert LocationRelationshipsResponse(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customers():
    ROUTE = f"/customers/{CUSTOMER_ID}/adp-customers"
    method = test_client.get
    perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
        auth_overrides.DeveloperToken,
    )
    response_codes = (200, 200, 200, 401, 401, 200)
    assert len(perms) == len(response_codes)
    for perm, rc in zip(perms, response_codes):
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = method(ROUTE)
        assert response.status_code == rc
        if rc == 200:
            assert RelatedCustomerResponse(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customers():
    ROUTE = f"/customers/{CUSTOMER_ID}/relationships/adp-customers"
    method = test_client.get
    perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
        auth_overrides.DeveloperToken,
    )
    response_codes = (200, 200, 200, 401, 401, 200)
    assert len(perms) == len(response_codes)
    for perm, rc in zip(perms, response_codes):
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = method(ROUTE)
        assert response.status_code == rc
        if rc == 200:
            assert CustomersRelResp(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customer_terms():
    ROUTE = f"/customers/{CUSTOMER_ID}/adp-customer-terms"
    method = test_client.get
    perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
        auth_overrides.DeveloperToken,
    )
    response_codes = (200, 200, 200, 401, 401, 200)
    assert len(perms) == len(response_codes)
    for perm, rc in zip(perms, response_codes):
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = method(ROUTE)
        assert response.status_code == rc
        if rc == 200:
            assert RelatedADPCustomerTermsResp(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customer_terms():
    ROUTE = f"/customers/{CUSTOMER_ID}/relationships/adp-customer-terms"
    method = test_client.get
    perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
        auth_overrides.DeveloperToken,
    )
    response_codes = (200, 200, 200, 401, 401, 200)
    assert len(perms) == len(response_codes)
    for perm, rc in zip(perms, response_codes):
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = method(ROUTE)
        assert response.status_code == rc
        if rc == 200:
            assert ADPCustomerTermsRelationshipsResp(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}
