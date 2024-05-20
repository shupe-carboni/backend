from pytest import mark
from fastapi.testclient import TestClient
from app.main import app
from app.adp.models import (
    CoilProgResp,
    AirHandlerProgResp,
    CoilProgRObj,
    AirHandlerProgRObj,
)
from app.db import Stage
from app.jsonapi.sqla_models import ADPCoilProgram, ADPAHProgram
from app.auth import authenticate_auth0_token
from tests import auth_overrides
import pandas as pd

test_client = TestClient(app)


class TestRequest:
    def __init__(self, json: dict, url: str) -> None:
        self.json = json
        self.url = url

    def keys(self) -> list[str]:
        return ["json", "url"]

    def __getitem__(self, key: str) -> dict | str:
        match key:
            case "json":
                return self.json
            case "url":
                return self.url


ADP_CUSTOMER_ID = 59  # TEST CUSTOMER
VALID_COIL_PRODUCT_ID = 483
INVALID_COIL_PRODUCT_ID = 1  # invalid for the customer but not SCA
VALID_AH_PRODUCT_ID = 247
INVALID_AH_PRODUCT_ID = 1  # invalid for the customer but not SCA

PATH_PREFIX = "/adp"
COIL_PROGS = ADPCoilProgram.__jsonapi_type_override__
AH_PROGS = ADPAHProgram.__jsonapi_type_override__
PRICED_MODELS = pd.read_csv("./tests/model_pricing_examples.csv")
TEST_MODEL = "HE32924D175B1605AP"

# AH Change Requests
VALID_AH_CHANGE_REQ = TestRequest(
    json={
        "data": {
            "id": VALID_AH_PRODUCT_ID,
            "type": AH_PROGS,
            "attributes": {"stage": Stage.ACTIVE},
            "relationships": {
                "adp-customers": {
                    "data": {"id": ADP_CUSTOMER_ID, "type": "adp-customers"}
                }
            },
        }
    },
    url=f"{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}",
)
CUSTOMER_ID_WRONG_AH = TestRequest(
    json={
        "data": {
            "id": VALID_AH_PRODUCT_ID,
            "type": AH_PROGS,
            "attributes": {"stage": Stage.ACTIVE},
            "relationships": {
                "adp-customers": {
                    "data": {"id": ADP_CUSTOMER_ID + 1, "type": "adp-customers"}
                }
            },
        }
    },
    url=f"{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}",
)
RESET_AH_STATUS = TestRequest(
    json={
        "data": {
            "id": VALID_AH_PRODUCT_ID,
            "type": AH_PROGS,
            "attributes": {"stage": Stage.REMOVED},
            "relationships": {
                "adp-customers": {
                    "data": {"id": ADP_CUSTOMER_ID, "type": "adp-customers"}
                }
            },
        }
    },
    url=f"{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}",
)
PRODUCT_NOT_ASSOC_W_CUSTOMER_AH = TestRequest(
    json={
        "data": {
            "id": INVALID_AH_PRODUCT_ID,
            "type": AH_PROGS,
            "attributes": {"stage": Stage.ACTIVE},
            "relationships": {
                "adp-customers": {
                    "data": {"id": ADP_CUSTOMER_ID, "type": "adp-customers"}
                }
            },
        }
    },
    url=f"{PATH_PREFIX}/{AH_PROGS}/{INVALID_AH_PRODUCT_ID}",
)

# COIL Change Requests
VALID_COIL_CHANGE_REQ = TestRequest(
    json={
        "data": {
            "id": VALID_COIL_PRODUCT_ID,
            "type": COIL_PROGS,
            "attributes": {"stage": Stage.REMOVED},
            "relationships": {
                "adp-customers": {
                    "data": {"id": ADP_CUSTOMER_ID, "type": "adp-customers"}
                }
            },
        }
    },
    url=f"{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}",
)
CUSTOMER_ID_WRONG_COIL = TestRequest(
    json={
        "data": {
            "id": VALID_COIL_PRODUCT_ID,
            "type": COIL_PROGS,
            "attributes": {"stage": Stage.REMOVED},
            "relationships": {
                "adp-customers": {
                    "data": {"id": ADP_CUSTOMER_ID + 1, "type": "adp-customers"}
                }
            },
        }
    },
    url=f"{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}",
)
RESET_COIL_STATUS = TestRequest(
    json={
        "data": {
            "id": VALID_COIL_PRODUCT_ID,
            "type": COIL_PROGS,
            "attributes": {"stage": Stage.ACTIVE},
            "relationships": {
                "adp-customers": {
                    "data": {"id": ADP_CUSTOMER_ID, "type": "adp-customers"}
                }
            },
        }
    },
    url=f"{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}",
)
PRODUCT_NOT_ASSOC_W_CUSTOMER_COIL = TestRequest(
    json={
        "data": {
            "id": INVALID_COIL_PRODUCT_ID,
            "type": COIL_PROGS,
            "attributes": {"stage": Stage.ACTIVE},
            "relationships": {
                "adp-customers": {
                    "data": {"id": ADP_CUSTOMER_ID, "type": "adp-customers"}
                }
            },
        }
    },
    url=f"{PATH_PREFIX}/{COIL_PROGS}/{INVALID_COIL_PRODUCT_ID}",
)


def test_collection_filtering():
    """this is dependent on the data - in that we expect more than one customer to have data to return"""
    ## coil programs is the example
    ## I care only about the id numbers in "included", no other data
    trimmed_data_req = (
        "/adp/adp-coil-programs"
        "?fields_adp_customers=id"
        "&include=adp-customers"
        "&fields_adp_coil_programs=id"
    )
    app.dependency_overrides[authenticate_auth0_token] = (
        auth_overrides.CustomerStandardToken
    )
    response = test_client.get(trimmed_data_req)
    ## if filtering is working, only 1 customer id should be represented in the results
    customer_ids_in_result = set([x["id"] for x in response.json()["included"]])
    assert len(customer_ids_in_result) == 1
    assert customer_ids_in_result.pop() == ADP_CUSTOMER_ID

    ## now check that an admin gets more than one customer's data
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    response = test_client.get(trimmed_data_req)
    customer_ids_in_result = set([x["id"] for x in response.json()["included"]])
    assert len(customer_ids_in_result) > 1

    ## check that a developer sees only the test customer as well
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.DeveloperToken
    response = test_client.get(trimmed_data_req)
    ## if filtering is working, only 1 customer id should be represented in the results
    customer_ids_in_result = set([x["id"] for x in response.json()["included"]])
    assert len(customer_ids_in_result) == 1
    assert customer_ids_in_result.pop() == ADP_CUSTOMER_ID


@mark.parametrize(
    "model,price",
    list(zip(PRICED_MODELS.model_number.to_list(), PRICED_MODELS.price.to_list())),
)
def test_model_zero_discount_pricing(model, price):
    """make sure all reference models are priced correctly by the parsers on zero_discount_price"""
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    # id zero with sca employee perms or above triggers zero discount price-only, ignores the id for customer pricing
    url = "/adp/model-lookup/0?model_num="
    resp = test_client.get(url + str(model))
    assert resp.status_code == 200
    assert resp.json()["zero-discount-price"] == price


def test_model_lookup():
    sca_perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
    )
    for sca_perm in sca_perms:
        app.dependency_overrides[authenticate_auth0_token] = sca_perm
        base_url = f"{PATH_PREFIX}/model-lookup/"
        zero_id = base_url + "0"
        real_id = base_url + f"{ADP_CUSTOMER_ID}"
        response = test_client.get(zero_id + f"?model_num={TEST_MODEL}")
        assert response.status_code == 200
        assert "zero-discount-price" in response.json().keys()
        assert "net-price" not in response.json().keys()
        response = test_client.get(real_id + f"?model_num={TEST_MODEL}")
        assert response.status_code == 200
        assert "zero-discount-price" in response.json().keys()
        assert "net-price" in response.json().keys()
        app.dependency_overrides[authenticate_auth0_token] = {}

    customer_perms = (
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
    )
    pricing = (True, True, False)
    for customer_perm, show_pricing in zip(customer_perms, pricing):
        app.dependency_overrides[authenticate_auth0_token] = customer_perm
        base_url = f"{PATH_PREFIX}/model-lookup/"
        zero_id = base_url + "0"
        real_id = base_url + f"{ADP_CUSTOMER_ID}"
        invalid_id = base_url + f"{ADP_CUSTOMER_ID+1}"
        response = test_client.get(zero_id + f"?model_num={TEST_MODEL}")
        assert response.status_code == 401
        response = test_client.get(real_id + f"?model_num={TEST_MODEL}")
        assert response.status_code == 200
        if show_pricing:
            zero_discount_price = "zero-discount-price" in response.json().keys()
            net_price = "net-price" in response.json().keys()
        else:
            zero_discount_price = "zero-discount-price" not in response.json().keys()
            net_price = "net-price" not in response.json().keys()
        assert zero_discount_price
        assert net_price
        response = test_client.get(invalid_id + f"?model_num={TEST_MODEL}")
        assert response.status_code == 401
        app.dependency_overrides[authenticate_auth0_token] = {}


## SCA


def test_customer_coil_program_collection_as_sca():
    sca_perms = (auth_overrides.AdminToken, auth_overrides.SCAEmployeeToken)
    for perm in sca_perms:
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = test_client.get(f"{PATH_PREFIX}/{COIL_PROGS}")
        assert response.status_code == 200, response.json()
        assert CoilProgResp(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_coil_program_resource_as_sca():
    sca_perms = (auth_overrides.AdminToken, auth_overrides.SCAEmployeeToken)
    for perm in sca_perms:
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = test_client.get(
            f"{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}"
        )
        assert response.status_code == 200
        assert CoilProgResp(**response.json())
        assert isinstance(CoilProgResp(**response.json()).data, CoilProgRObj)
        response = test_client.get(
            f"{PATH_PREFIX}/{COIL_PROGS}/{INVALID_COIL_PRODUCT_ID}"
        )
        assert response.status_code == 200
        assert CoilProgResp(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_coil_program_modification_as_sca():
    sca_perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
    )
    for sca_perm in sca_perms:
        app.dependency_overrides[authenticate_auth0_token] = sca_perm
        pre_mod_response = test_client.get(VALID_COIL_CHANGE_REQ.url)
        assert pre_mod_response.json()["data"]["attributes"]["stage"] == Stage.ACTIVE
        try:
            # good request
            response = test_client.patch(**VALID_COIL_CHANGE_REQ)
            assert response.status_code == 200
            assert AirHandlerProgResp(**response.json())
            assert response.json()["data"]["attributes"]["stage"] == Stage.REMOVED

            # bad request - product ID is not associated with the customer
            response = test_client.patch(**PRODUCT_NOT_ASSOC_W_CUSTOMER_COIL)
            assert response.status_code == 401
        finally:
            test_client.patch(**RESET_COIL_STATUS)
            app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_ah_program_collection_as_sca():
    sca_perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
    )
    for sca_perm in sca_perms:
        app.dependency_overrides[authenticate_auth0_token] = sca_perm
        response = test_client.get(f"{PATH_PREFIX}/{AH_PROGS}")
        assert response.status_code == 200
        assert AirHandlerProgResp(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_ah_program_resource_as_sca():
    sca_perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
    )
    for sca_perm in sca_perms:
        app.dependency_overrides[authenticate_auth0_token] = sca_perm
        response = test_client.get(f"{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}")
        assert response.status_code == 200
        assert AirHandlerProgResp(**response.json())
        assert isinstance(
            AirHandlerProgResp(**response.json()).data, AirHandlerProgRObj
        )
        response = test_client.get(f"{PATH_PREFIX}/{AH_PROGS}/{INVALID_AH_PRODUCT_ID}")
        assert response.status_code == 200
        assert AirHandlerProgResp(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_ah_program_modification_as_sca():
    sca_perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
    )
    for sca_perm in sca_perms:
        app.dependency_overrides[authenticate_auth0_token] = sca_perm
        pre_mod_response = test_client.get(VALID_AH_CHANGE_REQ.url)
        assert pre_mod_response.json()["data"]["attributes"]["stage"] == Stage.REMOVED
        try:
            # good request
            response = test_client.patch(**VALID_AH_CHANGE_REQ)
            assert response.status_code == 200
            assert AirHandlerProgResp(**response.json())
            assert response.json()["data"]["attributes"]["stage"] == Stage.ACTIVE

            # bad request - product ID is not associated with the customer
            response = test_client.patch(**PRODUCT_NOT_ASSOC_W_CUSTOMER_AH)
            assert response.status_code == 401
        finally:
            test_client.patch(**RESET_AH_STATUS)
            app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_program_resource_delete():
    perms = (
        auth_overrides.SCAEmployeeToken,
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
    )
    for perm in perms:
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = test_client.delete(f"{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}")
        assert response.status_code == 401
        response = test_client.delete(
            f"{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}"
        )
        assert response.status_code == 401


## CUSTOMER ADMIN


def test_customer_coil_program_collection_as_customer():
    perms = (
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
    )
    for perm in perms:
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = test_client.get(f"{PATH_PREFIX}/{COIL_PROGS}")
        assert response.status_code == 200
        assert CoilProgResp(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_coil_program_resource_as_customer():
    perms = (
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
    )
    for perm in perms:
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = test_client.get(
            f"{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}"
        )
        assert response.status_code == 200
        assert CoilProgResp(**response.json())
        assert isinstance(CoilProgResp(**response.json()).data, CoilProgRObj)
        response = test_client.get(
            f"{PATH_PREFIX}/{COIL_PROGS}/{INVALID_COIL_PRODUCT_ID}"
        )
        assert response.status_code == 204
        assert response.content == str("").encode()
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_ah_program_collection_as_customer():
    perms = (
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
    )
    for perm in perms:
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = test_client.get(f"{PATH_PREFIX}/{AH_PROGS}")
        assert response.status_code == 200, response.text
        assert AirHandlerProgResp(**response.json())
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_ah_program_resource_as_customer():
    perms = (
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
    )
    for perm in perms:
        app.dependency_overrides[authenticate_auth0_token] = perm
        response = test_client.get(f"{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}")
        assert response.status_code == 200
        assert AirHandlerProgResp(**response.json())
        response = test_client.get(f"{PATH_PREFIX}/{AH_PROGS}/{INVALID_AH_PRODUCT_ID}")
        assert response.status_code == 204
        assert response.content == str("").encode()
        app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_ah_program_modification_as_customer():
    customer_perms = (
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
    )
    for customer_perm in customer_perms:
        app.dependency_overrides[authenticate_auth0_token] = customer_perm
        pre_mod_response = test_client.get(VALID_AH_CHANGE_REQ.url)
        assert pre_mod_response.json()["data"]["attributes"]["stage"] == Stage.REMOVED
        try:
            # good request
            response = test_client.patch(**VALID_AH_CHANGE_REQ)
            assert response.status_code == 200
            assert AirHandlerProgResp(**response.json())
            assert response.json()["data"]["attributes"]["stage"] == Stage.ACTIVE

            # bad request - invalid customer_id - do not reassign your product to someone else
            response = test_client.patch(**CUSTOMER_ID_WRONG_AH)
            assert response.status_code == 401
            # bad request - invalid product_id - do not allow reassignment of other's product
            response = test_client.patch(**PRODUCT_NOT_ASSOC_W_CUSTOMER_AH)
            assert response.status_code == 401
        finally:
            test_client.patch(**RESET_AH_STATUS)
            app.dependency_overrides[authenticate_auth0_token] = {}


def test_customer_coil_program_modification_as_customer():
    customer_perms = (
        auth_overrides.CustomerAdminToken,
        auth_overrides.CustomerManagerToken,
        auth_overrides.CustomerStandardToken,
    )
    for customer_perm in customer_perms:
        app.dependency_overrides[authenticate_auth0_token] = customer_perm
        pre_mod_response = test_client.get(VALID_COIL_CHANGE_REQ.url)
        assert pre_mod_response.json()["data"]["attributes"]["stage"] == Stage.ACTIVE
        try:
            # good request
            response = test_client.patch(**VALID_COIL_CHANGE_REQ)
            assert response.status_code == 200
            assert AirHandlerProgResp(**response.json())
            assert response.json()["data"]["attributes"]["stage"] == Stage.REMOVED

            # bad request - invalid customer_id - do not reassign your product to someone else
            response = test_client.patch(**CUSTOMER_ID_WRONG_COIL)
            assert response.status_code == 401
            # bad request - invalid product_id - do not allow reassignment of other's product
            response = test_client.patch(**PRODUCT_NOT_ASSOC_W_CUSTOMER_COIL)
            assert response.status_code == 401
        finally:
            test_client.patch(**RESET_COIL_STATUS)
            app.dependency_overrides[authenticate_auth0_token] = {}
