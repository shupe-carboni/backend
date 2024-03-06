from fastapi.testclient import TestClient
from app.main import app
from app.customers.models import CustomerResponse
from app.customers.locations.models import RelatedLocationResponse, LocationRelationshipsResponse
from app.adp.models import (
    RelatedCustomerResponse,
    CustomersRelResp,
    RelatedADPCustomerTermsResp,
    ADPCustomerTermsRelationshipsResp
)
from app.auth import customers_perms_present, adp_perms_present
from tests import auth_overrides

# BUG should I really be using just ADP permissions for the adp relationships?

test_client = TestClient(app)
CUSTOMER_ID = 13 # NOTE should or can I randomize this?

## SCA ADMIN
def test_customer_collection_as_sca_admin():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_sca_admin('customers')
    response = test_client.get('/customers')
    assert response.status_code == 200
    assert CustomerResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_customer_resource_as_sca_admin():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_sca_admin('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}')
    assert response.status_code == 200
    assert CustomerResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_related_customer_locations_as_sca_admin():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_sca_admin('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/customer-locations')
    assert response.status_code == 200
    assert RelatedLocationResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_customer_locations_as_sca_admin():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_sca_admin('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/customer-locations')
    assert response.status_code == 200
    assert LocationRelationshipsResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_related_adp_customers_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/adp-customers')
    assert response.status_code == 200
    assert RelatedCustomerResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_adp_customers_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/adp-customers')
    assert response.status_code == 200
    assert CustomersRelResp(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_related_adp_customer_terms_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/adp-customer-terms')
    assert response.status_code == 200
    assert RelatedADPCustomerTermsResp(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_adp_customer_terms_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/adp-customer-terms')
    assert response.status_code == 200
    assert ADPCustomerTermsRelationshipsResp(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

"""SCA Employees don't have any distingished abilities compared to admin, meaning these tests are
    currently repeats of the admin tests, just with different permissions"""
def test_customer_collection_as_sca_employee():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_sca_employee('customers')
    response = test_client.get('/customers')
    assert response.status_code == 200
    assert CustomerResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_customer_resource_as_sca_employee():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_sca_employee('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}')
    assert response.status_code == 200
    assert CustomerResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_related_customer_locations_as_sca_employee():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_sca_employee('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/customer-locations')
    assert response.status_code == 200
    assert RelatedLocationResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_customer_locations_as_sca_employee():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_sca_employee('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/customer-locations')
    assert response.status_code == 200
    assert LocationRelationshipsResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_related_adp_customers_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/adp-customers')
    assert response.status_code == 200
    assert RelatedCustomerResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_adp_customers_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/adp-customers')
    assert response.status_code == 200
    assert CustomersRelResp(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_related_adp_customer_terms_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/adp-customer-terms')
    assert response.status_code == 200
    assert RelatedADPCustomerTermsResp(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_adp_customer_terms_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/adp-customer-terms')
    assert response.status_code == 200
    assert ADPCustomerTermsRelationshipsResp(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

"""Customer admins should be able to see info about themselves, but manager and standard customer permissions
    seem a little more tricky .. so I'm leaving those restrictewd for now"""
## ADMIN
def test_customer_collection_as_customer_admin():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_customer_admin('customers')
    response = test_client.get('/customers')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_customer_resource_as_customer_admin():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_customer_admin('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_related_customer_locations_as_customer_admin():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_customer_admin('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/customer-locations')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_customer_locations_as_customer_admin():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_customer_admin('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/customer-locations')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_related_adp_customers_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/adp-customers')
    assert response.status_code == 200
    assert RelatedCustomerResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_adp_customers_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/adp-customers')
    assert response.status_code == 200
    assert CustomersRelResp(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_related_adp_customer_terms_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/adp-customer-terms')
    assert response.status_code == 200
    assert RelatedADPCustomerTermsResp(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_adp_customer_terms_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/adp-customer-terms')
    assert response.status_code == 200
    assert ADPCustomerTermsRelationshipsResp(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

## MANAGER
def test_customer_collection_as_customer_manager():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_customer_manager('customers')
    response = test_client.get('/customers')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_customer_resource_as_customer_manager():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_customer_manager('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_related_customer_locations_as_customer_manager():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_customer_manager('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/customer-locations')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_customer_locations_as_customer_manager():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_customer_manager('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/customer-locations')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_related_adp_customers_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/adp-customers')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_adp_customers_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/adp-customers')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_related_adp_customer_terms_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/adp-customer-terms')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_adp_customer_terms_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/adp-customer-terms')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

## STANDARD
def test_customer_collection_as_customer_std():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_customer_std('customers')
    response = test_client.get('/customers')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_customer_resource_as_customer_std():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_customer_std('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_related_customer_locations_as_customer_std():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_customer_std('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/customer-locations')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_customer_locations_as_customer_std():
    app.dependency_overrides[customers_perms_present] = auth_overrides.auth_as_customer_std('customers')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/customer-locations')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_related_adp_customers_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/adp-customers')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_adp_customers_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/adp-customers')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_related_adp_customer_terms_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/adp-customer-terms')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_adp_customer_terms_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get(f'/customers/{CUSTOMER_ID}/relationships/adp-customer-terms')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}
