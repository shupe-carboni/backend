from fastapi.testclient import TestClient
from functools import partial
from app.main import app
from app.customers.models import CustomerResponse
from app.customers.locations.models import RelatedLocationResponse, LocationRelationshipsResponse
from app.auth import (
    customers_perms_present,
    adp_perms_present,
    perm_category_present,
    CustomersPermPriority,
    ADPPermPriority,
    Permissions
)

test_client = TestClient(app)

class AdminToken:
    def perm_level(category):
        return Permissions[category].value.sca_admin.value

class SCAEmployeeToken:
    def perm_level(category):
        return Permissions[category].value.sca_employee.value

class CustomerToken:
    def perm_level(category):
        return Permissions[category].value.customer_admin.value

def client_authenticated_as_sca_admin(perm_category):
    return partial(perm_category_present, AdminToken, perm_category)

def client_authenticated_as_sca_employee(perm_category):
    return partial(perm_category_present, SCAEmployeeToken, perm_category)

def client_authenticated_as_customer(perm_category):
    return partial(perm_category_present, CustomerToken, perm_category)


def test_customer_collection_as_sca_admin():
    app.dependency_overrides[customers_perms_present] = client_authenticated_as_sca_admin('customers')
    response = test_client.get('/customers')
    assert response.status_code == 200
    assert CustomerResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_customer_resource_as_sca_admin():
    app.dependency_overrides[customers_perms_present] = client_authenticated_as_sca_admin('customers')
    customer_id = 13 # NOTE should or can I randomize this?
    response = test_client.get(f'/customers/{customer_id}')
    assert response.status_code == 200
    assert CustomerResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_related_customer_locations_as_sca_admin():
    app.dependency_overrides[customers_perms_present] = client_authenticated_as_sca_admin('customers')
    customer_id = 13 # NOTE should or can I randomize this?
    response = test_client.get(f'/customers/{customer_id}/customer-locations')
    assert response.status_code == 200
    assert RelatedLocationResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_customer_locations_as_sca_admin():
    app.dependency_overrides[customers_perms_present] = client_authenticated_as_sca_admin('customers')
    customer_id = 13 # NOTE should or can I randomize this?
    customer_id = 13 # NOTE should or can I randomize this?
    response = test_client.get(f'/customers/{customer_id}/relationships/customer-locations')
    assert response.status_code == 501
    # assert LocationRelationshipsResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}


def test_related_adp_customers_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = client_authenticated_as_sca_admin('adp')
    customer_id = 13 # NOTE should or can I randomize this?
    response = test_client.get(f'/customers/{customer_id}/adp-customers')
    assert response.status_code == 501
    # assert RelatedLocationResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_adp_customers_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = client_authenticated_as_sca_admin('adp')
    customer_id = 13 # NOTE should or can I randomize this?
    response = test_client.get(f'/customers/{customer_id}/relationships/adp-customers')
    assert response.status_code == 501
    # assert LocationRelationshipsResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

"""SCA Employees don't have any distingished abilities compared to admin, meaning these tests are
    currently repeats of the admin tests, just with different permissions"""
def test_customer_collection_as_sca_emploee():
    app.dependency_overrides[customers_perms_present] = client_authenticated_as_sca_employee('customers')
    response = test_client.get('/customers')
    assert response.status_code == 200
    assert CustomerResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_customer_resource_as_sca_employee():
    app.dependency_overrides[customers_perms_present] = client_authenticated_as_sca_employee('customers')
    customer_id = 13 # NOTE should or can I randomize this?
    response = test_client.get(f'/customers/{customer_id}')
    assert response.status_code == 200
    assert CustomerResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_related_customer_locations_as_sca_emploee():
    app.dependency_overrides[customers_perms_present] = client_authenticated_as_sca_employee('customers')
    customer_id = 13 # NOTE should or can I randomize this?
    response = test_client.get(f'/customers/{customer_id}/customer-locations')
    assert response.status_code == 200
    assert RelatedLocationResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_customer_locations_as_sca_emploee():
    app.dependency_overrides[customers_perms_present] = client_authenticated_as_sca_employee('customers')
    customer_id = 13 # NOTE should or can I randomize this?
    response = test_client.get(f'/customers/{customer_id}/relationships/customer-locations')
    assert response.status_code == 501
    # assert LocationRelationshipsResponse(**response.json())
    app.dependency_overrides[customers_perms_present] = {}

"""Customers should always get a 401 on these endpoints"""
def test_customer_collection_as_customer():
    app.dependency_overrides[customers_perms_present] = client_authenticated_as_customer('customers')
    response = test_client.get('/customers')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_customer_resource_as_customer():
    app.dependency_overrides[customers_perms_present] = client_authenticated_as_customer('customers')
    customer_id = 13 # NOTE should or can I randomize this?
    response = test_client.get(f'/customers/{customer_id}')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_related_customer_locations_as_customer():
    app.dependency_overrides[customers_perms_present] = client_authenticated_as_customer('customers')
    customer_id = 13 # NOTE should or can I randomize this?
    response = test_client.get(f'/customers/{customer_id}/customer-locations')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}

def test_relationship_customer_locations_as_customer():
    app.dependency_overrides[customers_perms_present] = client_authenticated_as_customer('customers')
    customer_id = 13 # NOTE should or can I randomize this?
    response = test_client.get(f'/customers/{customer_id}/relationships/customer-locations')
    assert response.status_code == 401
    app.dependency_overrides[customers_perms_present] = {}