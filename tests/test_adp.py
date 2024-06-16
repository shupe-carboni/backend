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
from pprint import pprint
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


class mock_S3:
    async def upload_file(cls, file, destination):
        return


app.dependency_overrides[real_S3] = mock_S3

collections_endpoints = [
    "adp-coil-programs",
    "adp-ah-programs",
    "adp-material-group-discounts",
    "adp-snps",
    "adp-quotes",
]

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
            "attributes": {"stage": Stage.PROPOSED},
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

VALID_MAT_GRP_DISC_STAGE_CHANGE_REQ = TestRequest(
    json={
        "data": {
            "id": MAT_GRP_DISC_ID,
            "type": "adp-material-group-discounts",
            "attributes": {"stage": Stage.REJECTED},
            "relationships": {
                "adp-customers": {
                    "data": {"id": ADP_CUSTOMER_ID, "type": "adp-customers"}
                }
            },
        }
    },
    url=f"{PATH_PREFIX}/{ADP_MAT_GROUP_DISCOUNTS}/{MAT_GRP_DISC_ID}",
)
RESET_MAT_GRP_DISC_STAGE_CHANGE_REQ = TestRequest(
    json={
        "data": {
            "id": MAT_GRP_DISC_ID,
            "type": "adp-material-group-discounts",
            "attributes": {"stage": Stage.PROPOSED},
            "relationships": {
                "adp-customers": {
                    "data": {"id": ADP_CUSTOMER_ID, "type": "adp-customers"}
                }
            },
        }
    },
    url=f"{PATH_PREFIX}/{ADP_MAT_GROUP_DISCOUNTS}/{MAT_GRP_DISC_ID}",
)

VALID_SNP_STAGE_CHANGE_REQ = TestRequest(
    json={
        "data": {
            "id": SNP_ID,
            "type": "adp-snps",
            "attributes": {"stage": Stage.REJECTED},
            "relationships": {
                "adp-customers": {
                    "data": {"id": ADP_CUSTOMER_ID, "type": "adp-customers"}
                }
            },
        }
    },
    url=f"{PATH_PREFIX}/{ADP_SNPS}/{SNP_ID}",
)
RESET_SNP_STAGE_CHANGE_REQ = TestRequest(
    json={
        "data": {
            "id": SNP_ID,
            "type": "adp-snps",
            "attributes": {"stage": Stage.REMOVED},
            "relationships": {
                "adp-customers": {
                    "data": {"id": ADP_CUSTOMER_ID, "type": "adp-customers"}
                }
            },
        }
    },
    url=f"{PATH_PREFIX}/{ADP_SNPS}/{SNP_ID}",
)


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_valid_dl_link_reqs_for_everyone(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    url = str(
        Path(PATH_PREFIX)
        / "programs"
        / str(ADP_CUSTOMER_ID)
        / "get-download?stage=active"
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
        / "get-download?stage=active"
    )
    response = test_client.post(url)
    assert response.status_code == response_code


@mark.parametrize("resource", collections_endpoints)
def test_collection_filtering(resource: str):
    ## related adp customer id numbers only, no other data
    trimmed_data_req = (
        f"{PATH_PREFIX}/{resource}"
        "?fields_adp_customers=id"
        "&include=adp-customers"
        f"&fields_{resource.replace('-','_')}=id"
        "&page_number=0"
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
    url = f"{PATH_PREFIX}/model-lookup?customer_id=0&model_num="
    resp = test_client.get(url + str(model))
    assert resp.status_code == 200
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


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_new_coil(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    url = Path(PATH_PREFIX) / COIL_PROGS
    new_coil = {
        "data": {
            "type": "adp-coil-programs",
            "attributes": {"model-number": TEST_COIL_MODEL},
            "relationships": {
                "adp-customers": {
                    "data": {"type": "adp-customers", "id": ADP_CUSTOMER_ID}
                }
            },
        }
    }
    response = test_client.post(str(url), json=new_coil)
    assert response.status_code == response_code, pprint(response.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_new_ah(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    url = Path(PATH_PREFIX) / AH_PROGS
    new_ah = {
        "data": {
            "type": "adp-ah-programs",
            "attributes": {"model-number": TEST_AH_MODEL},
            "relationships": {
                "adp-customers": {
                    "data": {"type": "adp-customers", "id": ADP_CUSTOMER_ID}
                }
            },
        }
    }
    response = test_client.post(str(url), json=new_ah)
    assert response.status_code == response_code, pprint(response.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_new_part(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    url = Path(PATH_PREFIX) / "adp-program-parts"
    new_part = {
        "data": {
            "type": "adp-program-parts",
            "attributes": {"part-number": "165616601A"},
            "relationships": {
                "adp-customers": {
                    "data": {"type": "adp-customers", "id": ADP_CUSTOMER_ID}
                }
            },
        }
    }
    response = test_client.post(str(url), json=new_part)
    assert response.status_code == response_code, response.json()


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_customer_coil_program_collection(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    response = test_client.get(f"{PATH_PREFIX}/{COIL_PROGS}")
    assert response.status_code == response_code, pprint(response.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_customer_ah_program_collection(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    response = test_client.get(f"{PATH_PREFIX}/{AH_PROGS}")
    assert response.status_code == response_code, pprint(response.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_customer_coil_program_resource_for_everyone(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    response = test_client.get(f"{PATH_PREFIX}/{COIL_PROGS}/{VALID_COIL_PRODUCT_ID}")
    assert response.status_code == response_code


@mark.parametrize("perm,response_code", SCA_ONLY_EXCLUDING_DEV)
def test_customer_coil_program_resource_for_sca(perm, response_code):
    # this resource just returns no content (204) if a customer gives an invalid id
    if response_code == 401:
        response_code = 204
    app.dependency_overrides[authenticate_auth0_token] = perm
    response = test_client.get(f"{PATH_PREFIX}/{COIL_PROGS}/{INVALID_COIL_PRODUCT_ID}")
    assert response.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_customer_coil_program_modification(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    pre_mod_response = test_client.get(VALID_COIL_CHANGE_REQ.url)
    assert pre_mod_response.json()["data"]["attributes"]["stage"] == Stage.ACTIVE
    try:
        # good request
        response = test_client.patch(**VALID_COIL_CHANGE_REQ)
        assert response.status_code == response_code
        assert response.json()["data"]["attributes"]["stage"] == Stage.REMOVED

        # bad request - product ID is not associated with the customer
        response = test_client.patch(**PRODUCT_NOT_ASSOC_W_CUSTOMER_COIL)
        assert response.status_code == 401
    finally:
        test_client.patch(**RESET_COIL_STATUS)


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_customer_ah_program_resource_for_everyone(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    response = test_client.get(f"{PATH_PREFIX}/{AH_PROGS}/{VALID_AH_PRODUCT_ID}")
    assert response.status_code == response_code


@mark.parametrize("perm,response_code", SCA_ONLY_EXCLUDING_DEV)
def test_customer_ah_program_resource_for_sca(perm, response_code):
    # get resource returns no content (204) for id mismatch
    if response_code == 401:
        response_code = 204
    app.dependency_overrides[authenticate_auth0_token] = perm
    response = test_client.get(f"{PATH_PREFIX}/{AH_PROGS}/{INVALID_AH_PRODUCT_ID}")
    assert response.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_customer_ah_program_modification(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    pre_mod_response = test_client.get(VALID_AH_CHANGE_REQ.url)
    assert pre_mod_response.json()["data"]["attributes"]["stage"] == Stage.PROPOSED
    try:
        # good request
        response = test_client.patch(**VALID_AH_CHANGE_REQ)
        assert response.status_code == response_code
        assert response.json()["data"]["attributes"]["stage"] == Stage.ACTIVE

        # bad request - product ID is not associated with the customer
        response = test_client.patch(**PRODUCT_NOT_ASSOC_W_CUSTOMER_AH)
        assert response.status_code == 401
    finally:
        test_client.patch(**RESET_AH_STATUS)


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_customer_program_resource_delete(perm, response_code):
    new_ah = {
        "data": {
            "type": "adp-ah-programs",
            "attributes": {"model-number": TEST_AH_MODEL},
            "relationships": {
                "adp-customers": {
                    "data": {"type": "adp-customers", "id": ADP_CUSTOMER_ID}
                }
            },
        }
    }
    new_coil = {
        "data": {
            "type": "adp-coil-programs",
            "attributes": {"model-number": TEST_COIL_MODEL},
            "relationships": {
                "adp-customers": {
                    "data": {"type": "adp-customers", "id": ADP_CUSTOMER_ID}
                }
            },
        }
    }
    if response_code == 200:
        response_code = 204
    app.dependency_overrides[authenticate_auth0_token] = perm
    # Make a new AH
    response = test_client.post(f"{PATH_PREFIX}/{AH_PROGS}", json=new_ah)
    new_id = response.json()["data"]["id"]
    response = test_client.delete(
        f"{PATH_PREFIX}/{AH_PROGS}/{new_id}" f"?adp_customer_id={ADP_CUSTOMER_ID}"
    )
    assert response.status_code == 204, pprint(response.json())
    # Make a new Coil
    response = test_client.post(f"{PATH_PREFIX}/{COIL_PROGS}", json=new_coil)
    new_id = response.json()["data"]["id"]
    response = test_client.delete(
        f"{PATH_PREFIX}/{COIL_PROGS}/{new_id}" f"?adp_customer_id={ADP_CUSTOMER_ID}"
    )
    assert response.status_code == 204, pprint(response.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_related_mat_grp_disc(perm, response_code):
    url = str(
        Path(PATH_PREFIX)
        / "adp-customers"
        / str(ADP_CUSTOMER_ID)
        / "adp-material-group-discounts"
    )
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_mat_grp_disc_relationships(perm, response_code):
    url = str(
        Path(PATH_PREFIX)
        / "adp-customers"
        / str(ADP_CUSTOMER_ID)
        / "relationships"
        / "adp-material-group-discounts"
    )
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_mat_grp_disc_collection(perm, response_code):
    url = str(Path(PATH_PREFIX) / "adp-material-group-discounts")
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_mat_grp_disc_resource(perm, response_code):
    url = str(Path(PATH_PREFIX) / "adp-material-group-discounts" / str(MAT_GRP_DISC_ID))
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_mat_grp_disc_related_mat_grp(perm, response_code):
    url = str(
        Path(PATH_PREFIX)
        / "adp-material-group-discounts"
        / str(MAT_GRP_DISC_ID)
        / "adp-material-groups"
    )
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_mat_grp_disc_mat_grp_relationships(perm, response_code):
    url = str(
        Path(PATH_PREFIX)
        / "adp-material-group-discounts"
        / str(MAT_GRP_DISC_ID)
        / "relationships"
        / "adp-material-groups"
    )
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", SCA_ONLY_INCLUDING_DEV)
def test_customer_mat_grp_disc_stage_modification(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    pre_mod_response = test_client.get(VALID_MAT_GRP_DISC_STAGE_CHANGE_REQ.url)
    assert pre_mod_response.json()["data"]["attributes"]["stage"] == Stage.PROPOSED
    try:
        # good request
        response = test_client.patch(**VALID_MAT_GRP_DISC_STAGE_CHANGE_REQ)
        assert response.status_code == response_code
        if response_code == 200:
            assert response.json()["data"]["attributes"]["stage"] == Stage.REJECTED
    finally:
        test_client.patch(**RESET_MAT_GRP_DISC_STAGE_CHANGE_REQ)


@mark.parametrize("perm,response_code", SCA_ONLY_INCLUDING_DEV)
def test_create_and_del_mat_grp_disc(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    # make a new record to delete
    url = Path(PATH_PREFIX) / "adp-material-group-discounts"
    new_mat_grp_disc = {
        "data": {
            "type": "adp-material-group-discounts",
            "attributes": {"discount": randint(1, 99)},
            "relationships": {
                "adp-customers": {
                    "data": {"type": "adp-customers", "id": ADP_CUSTOMER_ID}
                },
                "adp-material-groups": {
                    "data": {"type": "adp-material-groups", "id": MAT_GRP_ID}
                },
            },
        }
    }
    response = test_client.post(str(url), json=new_mat_grp_disc)
    assert response.status_code == response_code, pprint(response.json())
    if response_code != 200:
        return
    new_id = response.json()["data"]["id"]
    url /= str(str(new_id) + f"?adp_customer_id={ADP_CUSTOMER_ID}")
    response = test_client.delete(str(url))
    assert response.status_code == 204


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_snp_collection(perm, response_code):
    url = str(Path(PATH_PREFIX) / "adp-snps")
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_an_snp(perm, response_code):
    url = str(Path(PATH_PREFIX) / "adp-snps" / str(417))
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_snp_related_adp_customers(perm, response_code):
    url = str(Path(PATH_PREFIX) / "adp-snps" / str(417) / "adp-customers")
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_snp_adp_customer_relationships(perm, response_code):
    url = str(
        Path(PATH_PREFIX) / "adp-snps" / str(417) / "relationships" / "adp-customers"
    )
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", SCA_ONLY_INCLUDING_DEV)
def test_create_and_del_snp(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    # make a new record to delete
    url = Path(PATH_PREFIX) / "adp-snps"
    new_snp = {
        "data": {
            "type": "adp-snps",
            "attributes": {"model": str(randint(1, 99)), "price": randint(1, 99)},
            "relationships": {
                "adp-customers": {
                    "data": {"type": "adp-customers", "id": ADP_CUSTOMER_ID}
                },
            },
        }
    }
    response = test_client.post(str(url), json=new_snp)
    assert response.status_code == response_code, pprint(response.json())
    if response_code != 200:
        return
    new_id = response.json()["data"]["id"]
    url /= str(new_id) + f"?adp_customer_id={ADP_CUSTOMER_ID}"
    response = test_client.delete(str(url))
    assert response.status_code == 204


@mark.parametrize("perm,response_code", SCA_ONLY_INCLUDING_DEV)
def test_customer_snp_stage_modification(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    pre_mod_response = test_client.get(VALID_SNP_STAGE_CHANGE_REQ.url)
    assert pre_mod_response.json()["data"]["attributes"]["stage"] == Stage.REMOVED
    try:
        # good request
        response = test_client.patch(**VALID_SNP_STAGE_CHANGE_REQ)
        assert response.status_code == response_code
        if response_code == 200:
            assert response.json()["data"]["attributes"]["stage"] == Stage.REJECTED
    finally:
        test_client.patch(**RESET_SNP_STAGE_CHANGE_REQ)


## ADP QUOTES
@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_quotes_collection(perm, response_code):
    url = str(Path(PATH_PREFIX) / "adp-quotes")
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_quote_resource(perm, response_code):
    url = str(Path(PATH_PREFIX) / "adp-quotes")
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url + "/1")
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_new_quote_no_files(perm: VerifiedToken, response_code):
    url = (
        str(Path(PATH_PREFIX) / "adp-quotes")
        + f"?adp_customer_id={ADP_TEST_CUSTOMER_ID}"
    )
    QN = randint(10000000, 99999999)
    app.dependency_overrides[authenticate_auth0_token] = perm
    new_quote = {
        "adp_quote_id": f"QN-{QN}",
        "job_name": "Test Job",
        "status": Stage("proposed"),
        "place_id": TEST_CUSTOMER_PLACE,
        "customer_location_id": TEST_CUSTOMER_LOCATION,
    }
    resp = test_client.post(url, data=new_quote)
    assert resp.status_code == response_code, pprint(resp.json())
    if perm.permissions >= auth_overrides.DeveloperToken.permissions:
        assert resp.json()["data"]["attributes"].get("adp-quote-id") is not None
    else:
        assert resp.json()["data"]["attributes"].get("adp-quote-id") is None


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_new_quote_w_plans_file(perm, response_code):
    url = (
        str(Path(PATH_PREFIX) / "adp-quotes")
        + f"?adp_customer_id={ADP_TEST_CUSTOMER_ID}"
    )
    QN = randint(10000000, 99999999)
    app.dependency_overrides[authenticate_auth0_token] = perm
    new_quote = {
        "adp_quote_id": f"QN-{QN}",
        "job_name": "Test Job",
        "status": Stage("proposed"),
        "place_id": TEST_CUSTOMER_PLACE,
        "customer_location_id": TEST_CUSTOMER_LOCATION,
    }
    plans_doc = (
        "job job job job at job, jb.pdf",
        bytes("hello world", encoding="utf-8"),
        "application/pdf",
    )
    resp = test_client.post(url, data=new_quote, files={"plans_doc": plans_doc})
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", SCA_ONLY)
def test_patch_quote(perm, response_code):
    url = str(Path(PATH_PREFIX) / "adp-quotes")
    app.dependency_overrides[authenticate_auth0_token] = perm
    sample_quote = test_client.get(
        url + "?page_size=1&page_number=1&include=adp-customers"
    ).json()["data"][0]
    QN = randint(1000, 9999)
    sample_quote["attributes"]["adp-quote-id"] = f"QN-{QN}"
    rel_keys_to_delete = list()
    for other_rel in sample_quote["relationships"]:
        if other_rel != "adp-customers":
            rel_keys_to_delete.append(other_rel)
    for rel in rel_keys_to_delete:
        del sample_quote["relationships"][rel]

    resp = test_client.patch(
        url + f"/{sample_quote['id']}", json=dict(data=sample_quote)
    )
    assert resp.status_code == response_code, resp.text


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_delete_quote(perm, response_code):
    url = str(Path(PATH_PREFIX) / "adp-quotes")
    QN = randint(1000000, 9999999)
    app.dependency_overrides[authenticate_auth0_token] = perm
    new_quote = {
        "adp_quote_id": f"QN-{QN}",
        "job_name": "Test Job",
        "expires_at": (datetime.today().date() + timedelta(days=90)),
        "status": Stage("proposed"),
        "place_id": TEST_CUSTOMER_PLACE,
        "customer_location_id": TEST_CUSTOMER_LOCATION,
    }
    resp = test_client.post(
        url + f"?adp_customer_id={ADP_TEST_CUSTOMER_ID}", data=new_quote
    )
    assert resp.status_code == response_code, pprint(resp.json())
    if resp.status_code == 200:
        resp = test_client.delete(
            url + f"/{resp.json()['data']['id']}?adp_customer_id={ADP_TEST_CUSTOMER_ID}"
        )
        assert resp.status_code == 204, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_related_adp_customer(perm, response_code):
    url = str(Path(PATH_PREFIX) / "adp-quotes" / "1" / "adp-customers")
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_related_adp_quote_products(perm, response_code):
    url = str(Path(PATH_PREFIX) / "adp-quotes" / "1" / "adp-quote-products")
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_related_places(perm, response_code):
    url = str(Path(PATH_PREFIX) / "adp-quotes" / "1" / "places")
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_related_customer_locations(perm, response_code):
    url = str(Path(PATH_PREFIX) / "adp-quotes" / "1" / "customer-locations")
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code
