from fastapi.testclient import TestClient
from app.main import app
from app.adp.models import (
    CoilProgResp,
    AirHandlerProgResp
)
from app.auth import adp_perms_present
from tests import auth_overrides

# BUG should I really be using just ADP permissions for the adp relationships?

test_client = TestClient(app)
# NOTE should or can I randomize this?
# customer ids are not explitly used. The filtering process behind the
# get_collection and get_resource implementations already selects for the 
# proper adp_customer_id values based on a mapping table
# coil customer id = 23
# ah customer id = 23
VALID_COIL_PRODUCT_ID = 159
INVALID_COIL_PRODUCT_ID = 1 # invalid for the customer but not SCA
VALID_AH_PRODUCT_ID = 50
INVALID_AH_PRODUCT_ID = 1 # invalid for the customer but not SCA


def test_customer_coil_program_collection_filtering():
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

## SCA ADMIN
def test_customer_coil_program_collection_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get('/adp/adp-coil-programs')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_resource_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get(f'/adp/adp-coil-programs/{VALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    response = test_client.get(f'/adp/adp-coil-programs/{INVALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_collection_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get('/adp/adp-ah-programs')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_resource_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get(f'/adp/adp-ah-programs/{VALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    response = test_client.get(f'/adp/adp-ah-programs/{INVALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

## SCA EMPLOYEE
def test_customer_coil_program_collection_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.get('/adp/adp-coil-programs')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_resource_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.get(f'/adp/adp-coil-programs/{VALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    response = test_client.get(f'/adp/adp-coil-programs/{INVALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_collection_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.get('/adp/adp-ah-programs')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_resource_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.get(f'/adp/adp-ah-programs/{VALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    response = test_client.get(f'/adp/adp-ah-programs/{INVALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

## CUSTOMER ADMIN
def test_customer_coil_program_collection_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    response = test_client.get('/adp/adp-coil-programs')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_resource_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    response = test_client.get(f'/adp/adp-coil-programs/{VALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    response = test_client.get(f'/adp/adp-coil-programs/{INVALID_COIL_PRODUCT_ID}')
    assert response.status_code == 204
    assert response.content == str('').encode()
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_collection_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    response = test_client.get('/adp/adp-ah-programs')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_resource_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    response = test_client.get(f'/adp/adp-ah-programs/{VALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    response = test_client.get(f'/adp/adp-ah-programs/{INVALID_AH_PRODUCT_ID}')
    assert response.status_code == 204
    assert response.content == str('').encode()
    app.dependency_overrides[adp_perms_present] = {}

## CUSTOMER MANAGER
def test_customer_coil_program_collection_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    response = test_client.get('/adp/adp-coil-programs')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_resource_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    response = test_client.get(f'/adp/adp-coil-programs/{VALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    response = test_client.get(f'/adp/adp-coil-programs/{INVALID_COIL_PRODUCT_ID}')
    assert response.status_code == 204
    assert response.content == str('').encode()
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_collection_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    response = test_client.get('/adp/adp-ah-programs')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_resource_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    response = test_client.get(f'/adp/adp-ah-programs/{VALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    response = test_client.get(f'/adp/adp-ah-programs/{INVALID_AH_PRODUCT_ID}')
    assert response.status_code == 204
    assert response.content == str('').encode()
    app.dependency_overrides[adp_perms_present] = {}

## CUSTOMER STANDARD
def test_customer_coil_program_collection_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get('/adp/adp-coil-programs')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_resource_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get(f'/adp/adp-coil-programs/{VALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    response = test_client.get(f'/adp/adp-coil-programs/{INVALID_COIL_PRODUCT_ID}')
    assert response.status_code == 204
    assert response.content == str('').encode()
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_collection_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get('/adp/adp-ah-programs')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_resource_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get(f'/adp/adp-ah-programs/{VALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    response = test_client.get(f'/adp/adp-ah-programs/{INVALID_AH_PRODUCT_ID}')
    assert response.status_code == 204
    assert response.content == str('').encode()
    app.dependency_overrides[adp_perms_present] = {}