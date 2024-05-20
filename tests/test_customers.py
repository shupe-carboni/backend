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

# BUG should I really be using just ADP permissions for the adp relationships?

test_client = TestClient(app)
CUSTOMER_ID = 999999  # NOTE associated with TEST CUSTOMER


## SCA ADMIN
def test_customer_collection_as_sca_admin():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    response = test_client.get("/customers")
    assert response.status_code == 200
    assert CustomerResponse(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_resource_as_sca_admin():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    response = test_client.get(f"/customers/{CUSTOMER_ID}")
    assert response.status_code == 200
    assert CustomerResponse(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_customer_locations_as_sca_admin():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    response = test_client.get(f"/customers/{CUSTOMER_ID}/customer-locations")
    assert response.status_code == 200
    assert RelatedLocationResponse(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_customer_locations_as_sca_admin():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    response = test_client.get(
        f"/customers/{CUSTOMER_ID}/relationships/customer-locations"
    )
    assert response.status_code == 200
    assert LocationRelationshipsResponse(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customers_as_sca_admin():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    response = test_client.get(f"/customers/{CUSTOMER_ID}/adp-customers")
    assert response.status_code == 200
    assert RelatedCustomerResponse(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customers_as_sca_admin():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    response = test_client.get(f"/customers/{CUSTOMER_ID}/relationships/adp-customers")
    assert response.status_code == 200
    assert CustomersRelResp(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customer_terms_as_sca_admin():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    response = test_client.get(f"/customers/{CUSTOMER_ID}/adp-customer-terms")
    assert response.status_code == 200
    assert RelatedADPCustomerTermsResp(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customer_terms_as_sca_admin():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    response = test_client.get(
        f"/customers/{CUSTOMER_ID}/relationships/adp-customer-terms"
    )
    assert response.status_code == 200
    assert ADPCustomerTermsRelationshipsResp(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


"""SCA Employees don't have any distingished abilities compared to admin, meaning these tests are
    currently repeats of the admin tests, just with different permissions"""


# SCA Customer
def test_customer_collection_as_sca_employee():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.SCAEmployeeToken
    response = test_client.get("/customers")
    assert response.status_code == 200
    assert CustomerResponse(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_resource_as_sca_employee():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.SCAEmployeeToken
    response = test_client.get(f"/customers/{CUSTOMER_ID}")
    assert response.status_code == 200
    assert CustomerResponse(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_customer_locations_as_sca_employee():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.SCAEmployeeToken
    response = test_client.get(f"/customers/{CUSTOMER_ID}/customer-locations")
    assert response.status_code == 200
    assert RelatedLocationResponse(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_customer_locations_as_sca_employee():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.SCAEmployeeToken
    response = test_client.get(
        f"/customers/{CUSTOMER_ID}/relationships/customer-locations"
    )
    assert response.status_code == 200
    assert LocationRelationshipsResponse(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customers_as_sca_employee():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.SCAEmployeeToken
    response = test_client.get(f"/customers/{CUSTOMER_ID}/adp-customers")
    assert response.status_code == 200
    assert RelatedCustomerResponse(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customers_as_sca_employee():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.SCAEmployeeToken
    response = test_client.get(f"/customers/{CUSTOMER_ID}/relationships/adp-customers")
    assert response.status_code == 200
    assert CustomersRelResp(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customer_terms_as_sca_employee():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.SCAEmployeeToken
    response = test_client.get(f"/customers/{CUSTOMER_ID}/adp-customer-terms")
    assert response.status_code == 200
    assert RelatedADPCustomerTermsResp(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customer_terms_as_sca_employee():
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.SCAEmployeeToken
    response = test_client.get(
        f"/customers/{CUSTOMER_ID}/relationships/adp-customer-terms"
    )
    assert response.status_code == 200
    assert ADPCustomerTermsRelationshipsResp(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


"""Customer admins should be able to see info about themselves, but manager and standard customer permissions
    seem a little more tricky .. so I'm leaving those restricted for now"""


## ADMIN
def test_customer_collection_as_customer_admin():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerAdminToken
    )
    response = test_client.get("/customers")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_resource_as_customer_admin():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerAdminToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_customer_locations_as_customer_admin():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerAdminToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}/customer-locations")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_customer_locations_as_customer_admin():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerAdminToken
    )
    response = test_client.get(
        f"/customers/{CUSTOMER_ID}/relationships/customer-locations"
    )
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customers_as_customer_admin():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerAdminToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}/adp-customers")
    assert response.status_code == 200
    assert RelatedCustomerResponse(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customers_as_customer_admin():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerAdminToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}/relationships/adp-customers")
    assert response.status_code == 200
    assert CustomersRelResp(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customer_terms_as_customer_admin():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerAdminToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}/adp-customer-terms")
    assert response.status_code == 200
    assert RelatedADPCustomerTermsResp(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customer_terms_as_customer_admin():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerAdminToken
    )
    response = test_client.get(
        f"/customers/{CUSTOMER_ID}/relationships/adp-customer-terms"
    )
    assert response.status_code == 200
    assert ADPCustomerTermsRelationshipsResp(**response.json())
    app.dependency_overrides[authenticate_auth0_token] = {}


## MANAGER
def test_customer_collection_as_customer_manager():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerManagerToken
    )
    response = test_client.get("/customers")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_resource_as_customer_manager():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerManagerToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_customer_locations_as_customer_manager():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerManagerToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}/customer-locations")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_customer_locations_as_customer_manager():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerManagerToken
    )
    response = test_client.get(
        f"/customers/{CUSTOMER_ID}/relationships/customer-locations"
    )
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customers_as_customer_manager():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerManagerToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}/adp-customers")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customers_as_customer_manager():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerManagerToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}/relationships/adp-customers")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customer_terms_as_customer_manager():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerManagerToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}/adp-customer-terms")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customer_terms_as_customer_manager():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerManagerToken
    )
    response = test_client.get(
        f"/customers/{CUSTOMER_ID}/relationships/adp-customer-terms"
    )
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


## STANDARD
def test_customer_collection_as_customer_std():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerStandardToken
    )
    response = test_client.get("/customers")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_resource_as_customer_std():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerStandardToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_customer_locations_as_customer_std():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerStandardToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}/customer-locations")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_customer_locations_as_customer_std():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerStandardToken
    )
    response = test_client.get(
        f"/customers/{CUSTOMER_ID}/relationships/customer-locations"
    )
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customers_as_customer_std():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerStandardToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}/adp-customers")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customers_as_customer_std():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerStandardToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}/relationships/adp-customers")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_related_adp_customer_terms_as_customer_std():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerStandardToken
    )
    response = test_client.get(f"/customers/{CUSTOMER_ID}/adp-customer-terms")
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}


def test_relationship_adp_customer_terms_as_customer_std():
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerStandardToken
    )
    response = test_client.get(
        f"/customers/{CUSTOMER_ID}/relationships/adp-customer-terms"
    )
    assert response.status_code == 401
    app.dependency_overrides[authenticate_auth0_token] = {}
