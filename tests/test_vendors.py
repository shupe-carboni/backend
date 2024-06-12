from fastapi.testclient import TestClient
from app.main import app
from app.auth import authenticate_auth0_token
from tests import auth_overrides
from pytest import mark
from random import randint, choice
from pprint import pprint
from app.jsonapi.sqla_models import SCAVendorInfo, SCAVendor
from pathlib import Path

test_client = TestClient(app)

VENDOR_RESOURCE = SCAVendor.__jsonapi_type_override__
VENDORS_PREFIX = Path(f"/{VENDOR_RESOURCE}")
INFO_RESOURCE = SCAVendorInfo.__jsonapi_type_override__
INFO_PREFIX = Path(f"/{INFO_RESOURCE}")

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


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_vendors_collection(perm, response_code):
    url = str(VENDORS_PREFIX)
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_vendor_resource(perm, response_code):
    url = str(VENDORS_PREFIX / "adp")
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", SCA_ONLY)
def test_new_vendor(perm, response_code):
    url = str(VENDORS_PREFIX)
    app.dependency_overrides[authenticate_auth0_token] = perm
    new_vendor = {
        "id": f"rand vend {randint(1000,9999)}",
        "type": VENDOR_RESOURCE,
        "attributes": {
            "name": f"RANDOM VENDOR {randint(1000,9999)}",
            "headquarters": "my backyard",
            "description": "test vendor automatically generated",
            "phone": randint(1000000000, 9999999999),
        },
    }
    resp = test_client.post(url, json=dict(data=new_vendor))
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", SCA_ONLY)
def test_mod_vendor(perm, response_code):
    url = str(VENDORS_PREFIX)
    app.dependency_overrides[authenticate_auth0_token] = perm
    pre_mod = test_client.get(url)
    rand_i, rand_id = choice(
        [
            (i, obj["id"])
            for i, obj in enumerate(pre_mod.json()["data"])
            if obj["attributes"]["name"].startswith("RANDOM")
        ]
    )
    current_number = pre_mod.json()["data"][rand_i]["attributes"]["phone"]
    new_number = current_number
    while new_number == current_number:
        new_number = randint(1000000000, 9999999999)
    mod_vendor = {
        "id": rand_id,
        "type": VENDOR_RESOURCE,
        "attributes": {
            "phone": new_number,
        },
    }
    url = str(VENDORS_PREFIX / str(rand_id))
    resp = test_client.patch(url, json=dict(data=mod_vendor))
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", SCA_ONLY)
def test_del_vendor(perm, response_code):
    # new vendor
    url = str(VENDORS_PREFIX)
    app.dependency_overrides[authenticate_auth0_token] = perm
    new_vendor = {
        "id": f"rand ven {randint(1000,9999)}",
        "type": VENDOR_RESOURCE,
        "attributes": {
            "name": f"RANDOM VENDOR {randint(1000,9999)}",
            "headquarters": "my backyard",
            "description": "test vendor automatically generated",
            "phone": randint(1000000000, 9999999999),
        },
    }
    resp = test_client.post(url, json=dict(data=new_vendor))
    if resp.status_code == 401:
        return
    new_vendor_id = resp.json()["data"]["id"]
    # make info for the vendor
    url = str(INFO_PREFIX)
    data = {
        "type": SCAVendorInfo.__jsonapi_type_override__,
        "attributes": {
            "category": "New category",
            "content": "more and more content. so much content.",
        },
        "relationships": {
            "vendors": {
                "data": {"id": str(6), "type": SCAVendor.__jsonapi_type_override__}
            }
        },
    }
    resp = test_client.post(url, json=dict(data=data))
    # delete
    url = str(VENDORS_PREFIX / str(new_vendor_id))
    resp = test_client.delete(url)
    assert resp.status_code == 204, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_vendor_info_collection(perm, response_code):
    url = str(INFO_PREFIX)
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_vendor_info_resource(perm, response_code):
    url = str(INFO_PREFIX / "1")
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_vendor_info_related_vendor(perm, response_code):
    url = str(INFO_PREFIX / "1" / SCAVendor.__jsonapi_type_override__)
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", ALL_ALLOWED)
def test_vendor_info_vendor_relationships(perm, response_code):
    url = str(INFO_PREFIX / "1" / "relationships" / SCAVendor.__jsonapi_type_override__)
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(url)
    assert resp.status_code == response_code, pprint(resp.json())


@mark.parametrize("perm,response_code", SCA_ONLY)
def test_new_vendor_info(perm, response_code):
    url = str(INFO_PREFIX)
    app.dependency_overrides[authenticate_auth0_token] = perm
    data = {
        "type": SCAVendorInfo.__jsonapi_type_override__,
        "attributes": {
            "category": "New category",
            "content": "more and more content. so much content.",
        },
        "relationships": {
            "vendors": {
                "data": {"id": str(6), "type": SCAVendor.__jsonapi_type_override__}
            }
        },
    }
    resp = test_client.post(url, json=dict(data=data))
    assert resp.status_code == response_code, pprint(resp.json())


mark.parametrize("perm,response_code", SCA_ONLY)


@mark.parametrize("perm,response_code", SCA_ONLY)
def test_mod_vendor_info(perm, response_code):
    app.dependency_overrides[authenticate_auth0_token] = perm
    url = str(INFO_PREFIX / "7")
    pre_mod = test_client.get(url).json()
    data = {
        "id": 7,
        "type": SCAVendorInfo.__jsonapi_type_override__,
        "attributes": {
            "category": f"New category {randint(10000,99999)}",
        },
        "relationships": {
            "vendors": {
                "data": {"id": str(6), "type": SCAVendor.__jsonapi_type_override__}
            }
        },
    }
    resp = test_client.patch(url, json=dict(data=data))
    assert resp.status_code == response_code, pprint(resp.json())
    if resp.status_code == 200:
        assert (
            resp.json()["data"]["attributes"]["category"]
            != pre_mod["data"]["attributes"]["category"]
        )


@mark.parametrize("perm,response_code", SCA_ONLY)
def test_del_vendor_info(perm, response_code):
    url = str(INFO_PREFIX)
    app.dependency_overrides[authenticate_auth0_token] = perm
    data = {
        "type": SCAVendorInfo.__jsonapi_type_override__,
        "attributes": {
            "category": "New category",
            "content": "more and more content. so much content.",
        },
        "relationships": {
            "vendors": {
                "data": {"id": str(6), "type": SCAVendor.__jsonapi_type_override__}
            }
        },
    }
    resp = test_client.post(url, json=dict(data=data))
    assert resp.status_code == response_code, pprint(resp.json())
    if resp.status_code == 200:
        url = str(INFO_PREFIX / (str(resp.json()["data"]["id"]) + "?vendor_id=6"))
        resp = test_client.delete(url)
        assert resp.status_code == 204


mark.parametrize("perm,response_code", SCA_ONLY)
