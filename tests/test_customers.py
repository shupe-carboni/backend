from fastapi.testclient import TestClient
from app.main import app
from app.customers.models import CustomerResponse
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
from tests import auth_overrides

test_client = TestClient(app)
CUSTOMER_ID = 999999  # NOTE associated with TEST CUSTOMER


def test_customer_collection():
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
        response = test_client.get("/customers")
        assert response.status_code == rc
        if rc == 200:
            assert CustomerResponse(**response.json())
            if dl:
                assert len(response.json()["data"]) == dl
            else:
                assert len(response.json()["data"]) > 1
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_resource():
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
        response = test_client.get(f"/customers/{CUSTOMER_ID}")
        assert response.status_code == rc
        if rc == 200:
            assert CustomerResponse(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_customer_locations():
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
        response = test_client.get(f"/customers/{CUSTOMER_ID}/customer-locations")
        assert response.status_code == rc
        if rc == 200:
            assert RelatedLocationResponse(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_customer_locations():
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
        response = test_client.get(
            f"/customers/{CUSTOMER_ID}/relationships/customer-locations"
        )
        assert response.status_code == rc
        if rc == 200:
            assert LocationRelationshipsResponse(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customers():
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
        response = test_client.get(f"/customers/{CUSTOMER_ID}/adp-customers")
        assert response.status_code == rc
        if rc == 200:
            assert RelatedCustomerResponse(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customers():
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
        response = test_client.get(
            f"/customers/{CUSTOMER_ID}/relationships/adp-customers"
        )
        assert response.status_code == rc
        if rc == 200:
            assert CustomersRelResp(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customer_terms():
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
        response = test_client.get(f"/customers/{CUSTOMER_ID}/adp-customer-terms")
        assert response.status_code == rc
        if rc == 200:
            assert RelatedADPCustomerTermsResp(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customer_terms():
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
        response = test_client.get(
            f"/customers/{CUSTOMER_ID}/relationships/adp-customer-terms"
        )
        assert response.status_code == rc
        if rc == 200:
            assert ADPCustomerTermsRelationshipsResp(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}
