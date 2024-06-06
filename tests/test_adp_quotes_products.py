from fastapi.testclient import TestClient
from app.main import app
from app.auth import authenticate_auth0_token
from tests import auth_overrides
from pytest import mark
from app.jsonapi.sqla_models import ADPQuoteProduct
from random import randint, choice
import string
from pprint import pprint

test_client = TestClient(app)

ADP_TEST_CUSTOMER_ID = 59
TEST_CUSTOMER_LOCATION = 5
TEST_CUSTOMER_PLACE = 4644585
TEST_COIL_MODEL = "HE32924D175B1605AP"

PATH_PREFIX = f"/adp/{ADPQuoteProduct.__jsonapi_type_override__}"

SCA_PERMS = (
    auth_overrides.AdminToken,
    auth_overrides.SCAEmployeeToken,
)
CUSTOMER_PERMS = (
    auth_overrides.CustomerAdminToken,
    auth_overrides.CustomerManagerToken,
    auth_overrides.CustomerStandardToken,
)
DEV_PERM = auth_overrides.DeveloperToken

ALL_ALLOWED = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [200] * (len(SCA_PERMS) + len(CUSTOMER_PERMS) + 1),
    )
)

SCA_ONLY = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [200, 200, 401, 401, 401, 200],
    )
)

NONE_ALLOWED = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [401, 401, 401, 401, 401, 401],
    )
)

NOT_IMPLEMENTED = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [501, 501, 501, 501, 501, 501],
    )
)


@mark.parametrize("perm,response_code", NOT_IMPLEMENTED)
def test_quote_products_collection(perm, response_code):
    url = PATH_PREFIX
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", NOT_IMPLEMENTED)
def test_quote_products_resource(perm, response_code):
    url = PATH_PREFIX + "/1"
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_new_quote_product(perm, response_code):
    url = PATH_PREFIX
    app.dependency_overrides[authenticate_auth0_token] = perm
    data = {
        "type": ADPQuoteProduct.__jsonapi_type_override__,
        "attributes": {
            "tag": "PRODUCT-1",
            "qty": randint(1, 100),
            "price": randint(100, 1500),
            "model-number": TEST_COIL_MODEL,
            "comp-model": "".join(
                choice(string.ascii_uppercase + string.digits) for _ in range(10)
            ),
        },
        "relationships": {"adp-quotes": {"data": {"type": "adp-quotes", "id": 1}}},
    }
    resp = test_client.post(url, json=dict(data=data))
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_mod_quote_product(perm, response_code):
    url = PATH_PREFIX
    app.dependency_overrides[authenticate_auth0_token] = perm
    pre_mod = test_client.get("/adp/adp-quotes/1/adp-quote-products").json()
    rand_obj_i, rand_obj_id = choice(
        [(i, obj["id"]) for i, obj in enumerate(pre_mod["data"])]
    )
    pre_mod_comp_model = pre_mod["data"][rand_obj_i]["attributes"]["comp-model"]
    new_comp_model = pre_mod_comp_model
    while pre_mod_comp_model == new_comp_model:
        new_comp_model = "".join(
            choice(string.ascii_uppercase + string.digits) for _ in range(10)
        )
    data = {
        "id": rand_obj_id,
        "type": ADPQuoteProduct.__jsonapi_type_override__,
        "attributes": {
            "comp-model": new_comp_model,
        },
        "relationships": {"adp-quotes": {"data": {"type": "adp-quotes", "id": 1}}},
    }
    resp = test_client.patch(url + f"/{rand_obj_id}", json=dict(data=data))
    assert resp.status_code == response_code, pprint(resp.json())
    if resp.status_code == 200:
        assert resp.json()["data"]["attributes"]["comp-model"] == new_comp_model


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_del_quote_product(perm, response_code):
    url = PATH_PREFIX
    app.dependency_overrides[authenticate_auth0_token] = perm
    # make new record first
    data = {
        "type": ADPQuoteProduct.__jsonapi_type_override__,
        "attributes": {
            "tag": "PRODUCT-1",
            "qty": randint(1, 100),
            "price": randint(100, 1500),
            "model-number": TEST_COIL_MODEL,
            "comp-model": "".join(
                choice(string.ascii_uppercase + string.digits) for _ in range(10)
            ),
        },
        "relationships": {"adp-quotes": {"data": {"type": "adp-quotes", "id": 1}}},
    }
    resp = test_client.post(url, json=dict(data=data))
    assert resp.status_code == response_code, pprint(resp.json())
    if resp.status_code == 200:
        # delete it
        del_resp = test_client.delete(url + f"/{resp.json()['data']['id']}?quote_id=1")
        assert del_resp.status_code == 204
