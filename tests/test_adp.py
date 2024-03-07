from fastapi.testclient import TestClient
from app.main import app
from app.adp.models import (
    CoilProgResp
)
from app.auth import adp_perms_present
from tests import auth_overrides

# BUG should I really be using just ADP permissions for the adp relationships?

test_client = TestClient(app)
CUSTOMER_ID = 13 # NOTE should or can I randomize this?

## SCA ADMIN
def test_customer_collection_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get('/adp/adp-coil-programs')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_collection_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get('/adp/adp-coil-programs')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_collection_filtering():
    """this is dependent on the data - in that we expect more than one customer to have data to return"""
    ## coil programs is the example
    ## I care only about the id numbers in "included", no other data
    trimmed_data_req = '/adp/adp-coil-programs?fields_adp_customers=id&include=adp-customers&fields_adp_coil_programs=id'
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get(trimmed_data_req)
    ## if filtering is working, only 1 customer id should be represented in the results
    assert len(set(map(lambda x: x['id'], response.json()['included']))) == 1
    ## now check that an admin gets more than one customer's data
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get(trimmed_data_req)
    assert len(set(map(lambda x: x['id'], response.json()['included']))) > 1