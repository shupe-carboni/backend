from pytest import mark
from fastapi.testclient import TestClient
from app.main import app
from app.adp.models import CoilProgResp, AirHandlerProgResp, CoilProgRObj, AirHandlerProgRObj
from app.db import Stage
from app.jsonapi.sqla_models import ADPCoilProgram, ADPAHProgram
from app.auth import adp_perms_present
from tests import auth_overrides
import pandas as pd

test_client = TestClient(app)
# get_collection and get_resource implementations already selects for the 
# proper adp_customer_id values based on a mapping table
# Customer ID is associated with TEST CUSTOMER
ADP_CUSTOMER_ID = 59 # TEST CUSTOMER
VALID_COIL_PRODUCT_ID = 483
INVALID_COIL_PRODUCT_ID = 1 # invalid for the customer but not SCA
VALID_AH_PRODUCT_ID = 247
INVALID_AH_PRODUCT_ID = 1 # invalid for the customer but not SCA

PATH_PREFIX = '/adp'
COIL_PROGS = ADPCoilProgram.__jsonapi_type_override__
AH_PROGS = ADPAHProgram.__jsonapi_type_override__
PRICED_MODELS = pd.read_csv('./tests/model_pricing_examples.csv')
TEST_MODEL = 'HE32924D175B1605AP'

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

@mark.parametrize("model,price", list(zip(PRICED_MODELS.model_number.to_list(), PRICED_MODELS.price.to_list())))
def test_model_zero_discount_pricing(model, price):
    """make sure all reference models are priced correctly by the parsers on zero_discount_price"""
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    # id zero with sca employee perms or above triggers zero discount price-only, ignores the id for customer pricing
    url = '/adp/model-lookup/0?model_num='
    resp = test_client.get(url+str(model))
    assert resp.status_code == 200
    assert resp.json()['zero-discount-price'] == price


## SCA ADMIN

def test_customer_coil_program_collection_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}')
    assert response.status_code == 200, response.json()
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_resource_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    assert isinstance(CoilProgResp(**response.json()).data, CoilProgRObj)
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}/{INVALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_modification_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    pre_mod_response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}')
    assert pre_mod_response.json()['data']['attributes']['stage'] == Stage.ACTIVE
    try:
        # good request
        body = {
            'data': {
                "id": VALID_COIL_PRODUCT_ID,
                "type": COIL_PROGS,
                'attributes':{
                    'stage': Stage.REMOVED
                }
            }
        }
        response = test_client.patch(f'{PATH_PREFIX}/{COIL_PROGS}/{ADP_CUSTOMER_ID}', json=body)
        assert response.status_code == 200
        assert CoilProgResp(**response.json())
        assert response.json()['data']['attributes']['stage'] == Stage.REMOVED
        # bad request
        body = {
            'data': {
                "id": INVALID_COIL_PRODUCT_ID,
                "type": COIL_PROGS,
                'attributes':{
                    'stage': Stage.REMOVED
                }
            }
        }
        response = test_client.patch(f'{PATH_PREFIX}/{COIL_PROGS}/{ADP_CUSTOMER_ID}', json=body)
        assert response.status_code == 404
    finally:
        body = {
            'data': {
                "id": VALID_COIL_PRODUCT_ID,
                "type": COIL_PROGS,
                'attributes':{
                    'stage': Stage.ACTIVE
                }
            }
        }
        test_client.patch(f'{PATH_PREFIX}/{COIL_PROGS}/{ADP_CUSTOMER_ID}', json=body)
        app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_collection_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_resource_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    assert isinstance(AirHandlerProgResp(**response.json()).data, AirHandlerProgRObj)
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}/{INVALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_modification_as_sca_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_admin('adp')
    pre_mod_response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}')
    assert pre_mod_response.json()['data']['attributes']['stage'] == Stage.REMOVED
    try:
        # good request
        body = {
            'data': {
                "id": VALID_AH_PRODUCT_ID,
                "type": AH_PROGS,
                'attributes':{
                    'stage': Stage.ACTIVE
                }
            }
        }
        response = test_client.patch(f'{PATH_PREFIX}/{AH_PROGS}/{ADP_CUSTOMER_ID}', json=body)
        assert response.status_code == 200
        assert AirHandlerProgResp(**response.json())
        assert response.json()['data']['attributes']['stage'] == Stage.ACTIVE
        # bad request
        body = {
            'data': {
                "id": INVALID_AH_PRODUCT_ID,
                "type": AH_PROGS,
                'attributes':{
                    'stage': Stage.ACTIVE
                }
            }
        }
        response = test_client.patch(f'{PATH_PREFIX}/{AH_PROGS}/{ADP_CUSTOMER_ID}', json=body)
        assert response.status_code == 404
    finally:
        body = {
            'data': {
                "id": VALID_AH_PRODUCT_ID,
                "type": AH_PROGS,
                'attributes':{
                    'stage': Stage.REMOVED
                }
            }
        }
        test_client.patch(f'{PATH_PREFIX}/{AH_PROGS}/{ADP_CUSTOMER_ID}', json=body)
        app.dependency_overrides[adp_perms_present] = {}

## SCA EMPLOYEE
def test_model_lookup_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    base_url = f'{PATH_PREFIX}/model-lookup/'
    zero_id = base_url + '0'
    real_id = base_url + f'{ADP_CUSTOMER_ID}'
    response = test_client.get(zero_id+f'?model_num={TEST_MODEL}')
    assert response.status_code == 200
    assert 'zero-discount-price' in response.json().keys()
    assert 'net-price' not in response.json().keys()
    response = test_client.get(real_id+f'?model_num={TEST_MODEL}')
    assert response.status_code == 200
    assert 'zero-discount-price' in response.json().keys()
    assert 'net-price' in response.json().keys()
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_collection_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_resource_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    assert isinstance(CoilProgResp(**response.json()).data, CoilProgRObj)
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}/{INVALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_resource_delete_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.delete(f'{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}')
    assert response.status_code == 401

def test_customer_ah_program_collection_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_resource_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}/{INVALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_resource_delete_as_sca_employee():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_sca_employee('adp')
    response = test_client.delete(f'{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}')
    assert response.status_code == 401
    # assert AirHandlerProgResp(**response.json())

## CUSTOMER ADMIN

def test_model_lookup_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    base_url = f'{PATH_PREFIX}/model-lookup/'
    zero_id = base_url + '0'
    real_id = base_url + f'{ADP_CUSTOMER_ID}'
    invalid_id = base_url + f'{ADP_CUSTOMER_ID+1}'
    response = test_client.get(zero_id+f'?model_num={TEST_MODEL}')
    assert response.status_code == 401
    response = test_client.get(real_id+f'?model_num={TEST_MODEL}')
    assert response.status_code == 200
    assert 'zero-discount-price' in response.json().keys()
    assert 'net-price' in response.json().keys()
    response = test_client.get(invalid_id+f'?model_num={TEST_MODEL}')
    assert response.status_code == 422
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_collection_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_resource_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    assert isinstance(CoilProgResp(**response.json()).data, CoilProgRObj)
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}/{INVALID_COIL_PRODUCT_ID}')
    assert response.status_code == 204
    assert response.content == str('').encode()
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_collection_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_resource_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}/{INVALID_AH_PRODUCT_ID}')
    assert response.status_code == 204
    assert response.content == str('').encode()
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_modification_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    # valid request
    body = {
        'data': {
            "id": VALID_AH_PRODUCT_ID,
            "type": AH_PROGS,
            'attributes':{
                'stage': Stage.ACTIVE
            }
        }
    }
    response = test_client.patch(f'{PATH_PREFIX}/{AH_PROGS}/{ADP_CUSTOMER_ID}', json=body)
    assert response.status_code == 401

def test_customer_coil_program_modification_as_customer_admin():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_admin('adp')
    # valid request
    body = {
        'data': {
            "id": VALID_COIL_PRODUCT_ID,
            "type": COIL_PROGS,
            'attributes':{
                'stage': Stage.ACTIVE
            }
        }
    }
    response = test_client.patch(f'{PATH_PREFIX}/{COIL_PROGS}/{ADP_CUSTOMER_ID}', json=body)
    assert response.status_code == 401

## CUSTOMER MANAGER

def test_model_lookup_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    base_url = f'{PATH_PREFIX}/model-lookup/'
    zero_id = base_url + '0'
    real_id = base_url + f'{ADP_CUSTOMER_ID}'
    invalid_id = base_url + f'{ADP_CUSTOMER_ID+1}'
    response = test_client.get(zero_id+f'?model_num={TEST_MODEL}')
    assert response.status_code == 401
    response = test_client.get(real_id+f'?model_num={TEST_MODEL}')
    assert response.status_code == 200
    assert 'zero-discount-price' in response.json().keys()
    assert 'net-price' in response.json().keys()
    response = test_client.get(invalid_id+f'?model_num={TEST_MODEL}')
    assert response.status_code == 422
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_collection_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_resource_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    assert isinstance(CoilProgResp(**response.json()).data, CoilProgRObj)
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}/{INVALID_COIL_PRODUCT_ID}')
    assert response.status_code == 204
    assert response.content == str('').encode()
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_collection_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_resource_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}/{INVALID_AH_PRODUCT_ID}')
    assert response.status_code == 204
    assert response.content == str('').encode()
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_modification_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    # valid request
    body = {
        'data': {
            "id": VALID_AH_PRODUCT_ID,
            "type": AH_PROGS,
            'attributes':{
                'stage': Stage.ACTIVE
            }
        }
    }
    response = test_client.patch(f'{PATH_PREFIX}/{AH_PROGS}/{ADP_CUSTOMER_ID}', json=body)
    assert response.status_code == 401

def test_customer_coil_program_modification_as_customer_manager():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_manager('adp')
    # valid request
    body = {
        'data': {
            "id": VALID_COIL_PRODUCT_ID,
            "type": COIL_PROGS,
            'attributes':{
                'stage': Stage.ACTIVE
            }
        }
    }
    response = test_client.patch(f'{PATH_PREFIX}/{COIL_PROGS}/{ADP_CUSTOMER_ID}', json=body)
    assert response.status_code == 401

## CUSTOMER STANDARD

def test_model_lookup_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    base_url = f'{PATH_PREFIX}/model-lookup/'
    zero_id = base_url + '0'
    real_id = base_url + f'{ADP_CUSTOMER_ID}'
    invalid_id = base_url + f'{ADP_CUSTOMER_ID+1}'
    response = test_client.get(zero_id+f'?model_num={TEST_MODEL}')
    assert response.status_code == 401
    response = test_client.get(real_id+f'?model_num={TEST_MODEL}')
    assert response.status_code == 200
    assert 'zero-discount-price' not in response.json().keys()
    assert 'net-price' not in response.json().keys()
    response = test_client.get(invalid_id+f'?model_num={TEST_MODEL}')
    assert response.status_code == 422
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_collection_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_coil_program_resource_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}')
    assert response.status_code == 200
    assert CoilProgResp(**response.json())
    assert isinstance(CoilProgResp(**response.json()).data, CoilProgRObj)
    response = test_client.get(f'{PATH_PREFIX}/{COIL_PROGS}/{INVALID_COIL_PRODUCT_ID}')
    assert response.status_code == 204
    assert response.content == str('').encode()
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_collection_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_resource_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}')
    assert response.status_code == 200
    assert AirHandlerProgResp(**response.json())
    response = test_client.get(f'{PATH_PREFIX}/{AH_PROGS}/{INVALID_AH_PRODUCT_ID}')
    assert response.status_code == 204
    assert response.content == str('').encode()
    app.dependency_overrides[adp_perms_present] = {}

def test_customer_ah_program_modification_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    # valid request
    body = {
        'data': {
            "id": VALID_AH_PRODUCT_ID,
            "type": AH_PROGS,
            'attributes':{
                'stage': Stage.ACTIVE
            }
        }
    }
    response = test_client.patch(f'{PATH_PREFIX}/{AH_PROGS}/{ADP_CUSTOMER_ID}', json=body)
    assert response.status_code == 401

def test_customer_coil_program_modification_as_customer_std():
    app.dependency_overrides[adp_perms_present] = auth_overrides.auth_as_customer_std('adp')
    # valid request
    body = {
        'data': {
            "id": VALID_COIL_PRODUCT_ID,
            "type": COIL_PROGS,
            'attributes':{
                'stage': Stage.ACTIVE
            }
        }
    }
    response = test_client.patch(f'{PATH_PREFIX}/{COIL_PROGS}/{ADP_CUSTOMER_ID}', json=body)
    assert response.status_code == 401
