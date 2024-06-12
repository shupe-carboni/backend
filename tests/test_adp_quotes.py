from fastapi.testclient import TestClient
from app.main import app
from app.auth import authenticate_auth0_token
from tests import auth_overrides
from pytest import mark
from random import randint
from datetime import datetime, timedelta
from app.db import Stage
from app.db import S3 as real_S3
from pprint import pprint

test_client = TestClient(app)

ADP_TEST_CUSTOMER_ID = 59
TEST_CUSTOMER_LOCATION = 5
TEST_CUSTOMER_PLACE = 4644585

PATH_PREFIX = "/vendors/adp/adp-quotes"

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


class mock_S3:
    async def upload_file(cls, file, destination):
        return


app.dependency_overrides[real_S3] = mock_S3


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_quotes_collection(perm, response_code):
    url = PATH_PREFIX
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_quote_resource(perm, response_code):
    url = PATH_PREFIX
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url + "/1")
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_new_quote_no_files(perm, response_code):
    url = PATH_PREFIX + f"?adp_customer_id={ADP_TEST_CUSTOMER_ID}"
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
    url = PATH_PREFIX + f"?adp_customer_id={ADP_TEST_CUSTOMER_ID}"
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
    url = PATH_PREFIX
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
    url = PATH_PREFIX
    QN = randint(1000, 9999)
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
    url = PATH_PREFIX + "/1/adp-customers"
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_related_adp_quote_products(perm, response_code):
    url = PATH_PREFIX + "/1/adp-quote-products"
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_related_places(perm, response_code):
    url = PATH_PREFIX + "/1/places"
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_related_customer_locations(perm, response_code):
    url = PATH_PREFIX + "/1/customer-locations"
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code
