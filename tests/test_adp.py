from pytest import mark
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.auth import authenticate_auth0_token
from app.db import S3 as real_S3
from tests import auth_overrides
import pandas as pd

# pytest doesn't like putting this under TYPE_CHECKING
from app.auth import VerifiedToken

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


ADP_CUSTOMER_ID = 55  # TEST CUSTOMER
PATH_PREFIX = "/vendors/model-lookup/adp"
PRICED_MODELS = pd.read_csv("./tests/assets/model_pricing_examples.csv")
TEST_COIL_MODEL = "HE32924D175B1605AP"
TEST_AH_MODEL = "SM312500"


class mock_S3:
    async def upload_file(cls, file, destination):
        return


app.dependency_overrides[real_S3] = mock_S3


@mark.parametrize(
    "model,price",
    list(zip(PRICED_MODELS.model_number.to_list(), PRICED_MODELS.price.to_list())),
)
def test_model_zero_discount_pricing(model, price):
    """make sure all reference models are priced correctly
    by the parsers on zero_discount_price"""
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    # id zero with sca employee perms or above triggers zero discount price-only,
    # ignores the id for customer pricing
    url = f"{PATH_PREFIX}?customer_id=0&model_number="
    resp = test_client.get(url + str(model))
    assert resp.status_code == 200, resp.content
    assert resp.json()["zero_discount_price"] == price


mapped_perms = [
    (auth_overrides.AdminToken, True, True, True),
    (auth_overrides.SCAEmployeeToken, True, True, True),
    (auth_overrides.CustomerAdminToken, False, True, False),
    (auth_overrides.CustomerManagerToken, False, True, False),
    (auth_overrides.CustomerStandardToken, False, False, False),
]


@mark.parametrize("token, no_cid, zero_disc, gating", mapped_perms)
def test_model_lookup(token, no_cid, zero_disc, gating):
    real_id = f"customer_id={ADP_CUSTOMER_ID}"
    invalid_id = f"customer_id={ADP_CUSTOMER_ID+1}"
    base_url = f"{PATH_PREFIX}"
    app.dependency_overrides[authenticate_auth0_token] = token

    response = test_client.get(base_url + f"?model_number={TEST_COIL_MODEL}")
    assert (response.status_code == 200) == no_cid, response.text

    response = test_client.get(base_url + f"?model_number={TEST_COIL_MODEL}&{real_id}")
    assert ("zero_discount_price" in response.json().keys()) == zero_disc

    response = test_client.get(
        base_url + f"?model_number={TEST_COIL_MODEL}&{invalid_id}"
    )
    assert (response.status_code == 200) == gating
    app.dependency_overrides[authenticate_auth0_token] = {}
