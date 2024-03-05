from fastapi.testclient import TestClient
from app.main import app
from app.customers.models import CustomerResponse
from app.customers.locations.models import RelatedLocationResponse, LocationRelationshipsResponse
from app.auth import (
    customers_perms_present,
    CustomersPermPriority
)

test_client = TestClient(app)
def client_authenticated_as_sca_admin():
    return {'customers': CustomersPermPriority.sca_admin}
app.dependency_overrides[customers_perms_present] = client_authenticated_as_sca_admin

def test_customer_collection():
    response = test_client.get('/customers')
    assert response.status_code == 200
    assert CustomerResponse(**response.json())

def test_related_customer_locations():
    customer_id = 13 # NOTE should or can I randomize this?
    response = test_client.get(f'/customers/{customer_id}/customer-locations')
    assert response.status_code == 200
    assert RelatedLocationResponse(**response.json())

def test_relationship_customer_locations():
    customer_id = 13 # NOTE should or can I randomize this?
    response = test_client.get(f'/customers/{customer_id}/relationships/customer-locations')
    assert response.status_code == 501
    # assert LocationRelationshipsResponse(**response.json())


