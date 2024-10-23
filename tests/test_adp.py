from pytest import mark
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.db import Stage
from app.jsonapi.sqla_models import (
    ADPCoilProgram,
    ADPAHProgram,
    ADPMaterialGroupDiscount,
    ADPSNP,
)
from app.auth import authenticate_auth0_token
from app.db import S3 as real_S3
from tests import auth_overrides
from datetime import datetime, timedelta
import pandas as pd
from pprint import pprint, pformat
from random import randint

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


ADP_CUSTOMER_ID = 59  # TEST CUSTOMER
ADP_TEST_CUSTOMER_ID = 59
TEST_CUSTOMER_LOCATION = 5
TEST_CUSTOMER_PLACE = 4644585
VALID_COIL_PRODUCT_ID = 483
INVALID_COIL_PRODUCT_ID = 1  # invalid for the customer but not SCA
VALID_AH_PRODUCT_ID = 293
INVALID_AH_PRODUCT_ID = 1  # invalid for the customer but not SCA
MAT_GRP_DISC_ID = 836
MAT_GRP_ID = "CA"
SNP_ID = 365

PATH_PREFIX = "/vendors/adp"
COIL_PROGS = ADPCoilProgram.__jsonapi_type_override__
AH_PROGS = ADPAHProgram.__jsonapi_type_override__
ADP_MAT_GROUP_DISCOUNTS = ADPMaterialGroupDiscount.__jsonapi_type_override__
ADP_SNPS = ADPSNP.__jsonapi_type_override__
PRICED_MODELS = pd.read_csv("./tests/model_pricing_examples.csv")
TEST_COIL_MODEL = "HE32924D175B1605AP"
TEST_AH_MODEL = "SM312500"


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

SCA_ONLY_INCLUDING_DEV = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [200, 200, 401, 401, 401, 200],
    )
)

SCA_ONLY_EXCLUDING_DEV = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [200, 200, 401, 401, 401, 401],
    )
)

SCA_ONLY = SCA_ONLY_INCLUDING_DEV

ALL_ALLOWED_EXCEPT_DEV = list(
    zip(
        [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM],
        [200, 200, 200, 200, 200, 401],
    )
)


class mock_S3:
    async def upload_file(cls, file, destination):
        return


app.dependency_overrides[real_S3] = mock_S3


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_valid_dl_link_reqs_for_everyone(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    url = str(
        Path(PATH_PREFIX) / "programs" / str(ADP_CUSTOMER_ID) / "download?stage=active"
    )
    response = test_client.post(url)
    assert response.status_code == response_code


@mark.parametrize("perm,response_code", SCA_ONLY_EXCLUDING_DEV)
def test_valid_dl_link_reqs_for_sca_only(perm, response_code):
    """change the id number to ensure SCA can do it, and customers cannot"""
    app.dependency_overrides[authenticate_auth0_token] = perm
    url = str(
        Path(PATH_PREFIX)
        / "programs"
        / str(ADP_CUSTOMER_ID + 1)
        / "download?stage=active"
    )
    response = test_client.post(url)
    assert response.status_code == response_code


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
    url = f"{PATH_PREFIX}/model-lookup?customer_id=0&model_num="
    resp = test_client.get(url + str(model))
    assert resp.status_code == 200, resp.content
    assert resp.json()["zero-discount-price"] == price


def test_model_lookup():
    sca_perms = (
        auth_overrides.AdminToken,
        auth_overrides.SCAEmployeeToken,
    )
    real_id = f"customer_id={ADP_CUSTOMER_ID}"
    base_url = f"{PATH_PREFIX}/model-lookup"
    for sca_perm in sca_perms:
        app.dependency_overrides[authenticate_auth0_token] = sca_perm
        response = test_client.get(base_url + f"?model_num={TEST_COIL_MODEL}")
        assert response.status_code == 200
        assert "zero-discount-price" in response.json().keys()
        assert "net-price" not in response.json().keys()
        response = test_client.get(base_url + f"?model_num={TEST_COIL_MODEL}&{real_id}")
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
        invalid_id = f"customer_id={ADP_CUSTOMER_ID+1}"
        response = test_client.get(base_url + f"?model_num={TEST_COIL_MODEL}")
        assert response.status_code == 401
        response = test_client.get(base_url + f"?model_num={TEST_COIL_MODEL}&{real_id}")
        assert response.status_code == 200
        if show_pricing:
            zero_discount_price = "zero-discount-price" in response.json().keys()
            net_price = "net-price" in response.json().keys()
        else:
            zero_discount_price = "zero-discount-price" not in response.json().keys()
            net_price = "net-price" not in response.json().keys()
        assert zero_discount_price
        assert net_price
        response = test_client.get(
            base_url + f"?model_num={TEST_COIL_MODEL}&{invalid_id}"
        )
        assert response.status_code == 401
        app.dependency_overrides[authenticate_auth0_token] = {}
