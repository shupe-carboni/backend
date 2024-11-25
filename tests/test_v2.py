from fastapi.testclient import TestClient
from pytest import mark, fixture
from random import random
from pprint import pformat
from httpx import Response
from pathlib import Path
from typing import Union, Optional
from dataclasses import dataclass, asdict, replace
from enum import StrEnum
from itertools import chain
from datetime import datetime, timedelta

from app.main import app
from app.auth import authenticate_auth0_token
from tests import auth_overrides
from app.jsonapi.sqla_models import *

test_client = TestClient(app)

ParameterizedStatusCodes = list[tuple[auth_overrides.Token, int]]

FUTURE_DATE = datetime.today() + timedelta(days=60)


class Arbitrary:
    def __init__(self, *args, **kwargs) -> None:
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.keys_ = [key for key in kwargs]

    def keys(self) -> list:
        return self.keys_

    def items(self) -> list[tuple]:
        return [(key, getattr(self, key)) for key in self.keys_]

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
        if key not in self.keys_:
            self.keys_.append(key)

    def __iter__(self):
        return iter(self.keys())


class Attributes(Arbitrary): ...


class Relationships(Arbitrary): ...


@dataclass
class Data:
    attributes: Attributes = None
    relationships: Relationships = None
    id: Optional[int | str] = None

    def __post_init__(self):
        self.attributes = {**self.attributes} if self.attributes else None
        if self.attributes:
            self.attributes = {
                k.replace("_", "-"): v for k, v in self.attributes.items() if k
            }
        self.relationships = {**self.relationships} if self.relationships else None
        if self.relationships:
            self.relationships = {
                k.replace("_", "-"): v for k, v in self.relationships.items() if k
            }

    @staticmethod
    def rand_num() -> int:
        return int((random() + 1) * 1000000000)

    def to_dict(self) -> dict:
        id_ = self.id
        attrs = self.attributes
        rels = self.relationships
        data_dict = asdict(self)

        match id_:
            case str():
                data_dict["id"] = id_.format(self.rand_num())

        if attrs:
            for k, v in attrs.items():
                if isinstance(v, str):
                    data_dict["attributes"][k] = v.format(self.rand_num())
        return dict(data=data_dict)


Parameter = tuple[auth_overrides.Token, int, str, str, Data | dict]


@dataclass
class Route:
    route: Path
    status_codes: tuple[ParameterizedStatusCodes, ParameterizedStatusCodes]
    post: Optional[Data] = None
    patch: Optional[Data] = None
    delete: Optional[dict[str, int | str]] = None

    def __post_init__(self) -> None:
        self.post_delete_status_codes, self.patch_status_codes = self.status_codes

    def parameterize(self) -> list[Parameter]:
        params: list[Parameter] = []
        post = self.post
        patch = self.patch
        delete = self.delete
        for status_code in self.post_delete_status_codes:
            perm, sc = status_code
            if post:
                new_item = (perm, sc, "post", str(self.route), post)
                params.append(new_item)
        for status_code in self.patch_status_codes:
            perm, sc = status_code
            if patch:
                new_item = (perm, sc, "patch", str(self.route), patch)
                params.append(new_item)
        for status_code in self.post_delete_status_codes:
            perm, sc = status_code
            del_item = (
                perm,
                sc,
                "delete",
                str(self.route),
                delete if delete else {},
            )
            params.append(del_item)
        return params


class HTTPReqType(StrEnum):
    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


VENDOR_RESOURCE = Vendor.__jsonapi_type_override__


class Shared:
    def __init__(self) -> None:
        self.data = {}

    def update(self, key, value) -> None:
        self.data.update({key: value})

    def get(self, key) -> Union[int | str | None]:
        return self.data.get(key)

    def clear(self) -> None:
        self.data.clear()


def try_return_json(response: Response) -> str:
    try:
        return pformat(response.json())
    except:
        return pformat(response.text)


@fixture(scope="module")
def shared():
    shared_state = Shared()
    yield shared_state
    shared_state.clear()


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

ALL_PERMS: list[auth_overrides.Token] = [*SCA_PERMS, *CUSTOMER_PERMS, DEV_PERM]

TEST_VENDOR_QUOTE_ID = 1  # ASSOCIATED WITH TEST_VENDOR_CUSTOMER_1
TEST_USER_ID = 2
TEST_CUSTOMER_LOCATION = 5
TEST_VENDOR_PRICING_BY_CLASS = 3638
TEST_VENDOR_PRICING_BY_CUSTOMER = 2696
TEST_VENDOR_PRICING_CLASS = 9
TEST_VENDOR_CUSTOMER_1_ID = 169
TEST_VENDOR_CUSTOMER_2_ID = 176
TEST_VENDOR_CUSTOMER_3_ID = 177
TEST_VENDOR_ATTR = str(4)
TEST_VENDOR_PRODUCT = str(2355)
TEST_VENDOR_PRODUCT_CLASS = str(51)
TEST_VENDOR_PRODUCT = str(2871)
MANAGER_CUSTOMER_IDS = [TEST_VENDOR_CUSTOMER_1_ID, TEST_VENDOR_CUSTOMER_2_ID]
ADMIN_CUSTOMER_IDS = [
    TEST_VENDOR_CUSTOMER_1_ID,
    TEST_VENDOR_CUSTOMER_2_ID,
    TEST_VENDOR_CUSTOMER_3_ID,
]

NOT_IMPLEMENTED = list(zip(ALL_PERMS, [501] * len(ALL_PERMS)))
ALL_ALLOWED = list(
    zip(
        ALL_PERMS,
        [200] * (len(SCA_PERMS) + len(CUSTOMER_PERMS) + 1),
    )
)

SCA_ONLY = list(
    zip(
        ALL_PERMS,
        [200, 200, 401, 401, 401, 200],
    )
)

EXCLUDE_BASE_CUSTOMER = list(
    zip(
        ALL_PERMS,
        [200, 200, 200, 200, 401, 200],
    )
)
VENDOR_CUSTOMER_IDS_BY_PERM = list(
    zip(
        ALL_PERMS,
        [
            ADMIN_CUSTOMER_IDS,
            ADMIN_CUSTOMER_IDS,
            ADMIN_CUSTOMER_IDS,
            MANAGER_CUSTOMER_IDS,
            [TEST_VENDOR_CUSTOMER_1_ID],
            ADMIN_CUSTOMER_IDS,
        ],
    )
)

VENDORS_PREFIX = Path(f"/v2/{VENDOR_RESOURCE}")
TEST_VENDOR = VENDORS_PREFIX / "TEST_VENDOR"
TEST_VENDOR_ATTR = str(4)
TEST_VENDOR_PRODUCT = str(2355)
TEST_VENDOR_PRODUCT_CLASS = str(51)
TEST_VENDOR_TEST_CUSTOMER = (
    TEST_VENDOR / "vendor-customers" / str(TEST_VENDOR_CUSTOMER_1_ID)
)
TEST_VENDOR_PRODUCT = str(2871)

ALL_ROUTES = [
    VENDORS_PREFIX,
    TEST_VENDOR,
    TEST_VENDOR / "vendors-attrs",
    TEST_VENDOR / "relationships" / "vendors-attrs",
    TEST_VENDOR / "vendor-products",
    TEST_VENDOR / "relationships" / "vendor-products",
    TEST_VENDOR / "vendor-product-classes",
    TEST_VENDOR / "relationships" / "vendor-product-classes",
    TEST_VENDOR / "vendor-pricing-classes",
    TEST_VENDOR / "relationships" / "vendor-pricing-classes",
    TEST_VENDOR / "vendor-customers",
    TEST_VENDOR / "relationships" / "vendor-customers",
    # chained static collections
    TEST_VENDOR / "vendors-attrs" / "vendors-attrs-changelog",
    TEST_VENDOR / "vendor-products" / "vendor-product-attrs",
    TEST_VENDOR / "vendor-customers" / "vendor-pricing-by-customer",
    TEST_VENDOR / "vendor-customers" / "vendor-product-class-discounts",
    TEST_VENDOR / "vendor-customers" / "vendor-customer-pricing-classes",
    TEST_VENDOR / "vendor-customers" / "vendor-quotes",
    TEST_VENDOR / "vendor-customers" / "customer-pricing-by-class",
    TEST_VENDOR / "vendor-customers" / "customer-pricing-by-customer",
    # chained dynamic resource/collections by object
    TEST_VENDOR / "vendors-attrs" / TEST_VENDOR_ATTR,
    TEST_VENDOR / "vendors-attrs" / TEST_VENDOR_ATTR / "vendors-attrs-changelog",
    TEST_VENDOR / "vendor-products" / TEST_VENDOR_PRODUCT,
    TEST_VENDOR / "vendor-products" / TEST_VENDOR_PRODUCT / "vendor-product-attrs",
    TEST_VENDOR_TEST_CUSTOMER,
    TEST_VENDOR_TEST_CUSTOMER / "vendor-pricing-by-customer",
    TEST_VENDOR_TEST_CUSTOMER / "vendor-product-class-discounts",
    TEST_VENDOR_TEST_CUSTOMER / "vendor-customer-pricing-classes",
    TEST_VENDOR_TEST_CUSTOMER / "vendor-quotes",
]
ROUTE_PERM_RESP_ALL_ALLOWED = [
    (str(route), perm, resp) for route in ALL_ROUTES for perm, resp in ALL_ALLOWED
]
CUSTOMER_SENSITIVE_COLLECTION_ROUTES = [
    TEST_VENDOR / "vendor-customers",
    TEST_VENDOR / "vendor-customers" / "vendor-pricing-by-customer",
    TEST_VENDOR / "vendor-customers" / "vendor-product-class-discounts",
    TEST_VENDOR / "vendor-customers" / "vendor-customer-pricing-classes",
    TEST_VENDOR / "vendor-customers" / "vendor-quotes",
]
ROUTE_FILTERING = [
    (str(route) + "?page_number=0", perm, ids)
    for route in CUSTOMER_SENSITIVE_COLLECTION_ROUTES
    for perm, ids in VENDOR_CUSTOMER_IDS_BY_PERM
]


@mark.parametrize("route,perm,response_code", ROUTE_PERM_RESP_ALL_ALLOWED)
def test_vendor_endpoint_response_codes(
    route: str, perm: auth_overrides.Token, response_code: int
):
    app.dependency_overrides[authenticate_auth0_token] = perm
    resp = test_client.get(route)
    no_content = resp.status_code == 204
    expected_code = resp.status_code == response_code
    internal_error = resp.status_code == 500
    assert expected_code or no_content, pformat(
        resp.text if internal_error else resp.json()
    )
    if expected_code and response_code == 200:
        resource = route.split("/")[-1]
        if "-" in resource:
            types_in_resp = set([record["type"] for record in resp.json()["data"]])
            assert len(types_in_resp) == 1 and types_in_resp.pop() == resource


@mark.parametrize("route,perm,ids", ROUTE_FILTERING)
def test_vendor_endpoint_response_content(
    route: str, perm: auth_overrides.Token, ids: list[int]
):
    """Return data ought to be filtered as expected based on the vendor in the path
    as well as the permission type"""
    app.dependency_overrides[authenticate_auth0_token] = perm
    if route.split("/")[-1] != "vendor-customers?page_number=0":
        route += "&include=vendor-customers"
        resp = test_client.get(route)
        returned_ids = sorted([customer["id"] for customer in resp.json()["included"]])
        assert returned_ids == ids
    else:
        resp = test_client.get(route)
        assert resp.status_code < 500, pformat(resp.text)
        returned_ids = sorted([customer["id"] for customer in resp.json()["data"]])
        match perm:
            case auth_overrides.AdminToken | auth_overrides.SCAEmployeeToken:
                assert set(returned_ids) >= set(ids) and len(returned_ids) > len(ids)
            case _:
                assert returned_ids == ids


post_patch_delete_outline = [
    Route(
        route=VENDORS_PREFIX,
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(id="TEST VENDOR {0}", attributes=Attributes(name=f"TEST VENDOR")),
        patch=Data(id="{0}", attributes=Attributes(headquarters="{0}")),
    ),
    Route(
        route=VENDORS_PREFIX / "vendors-attrs",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            attributes=Attributes(attr="test_attr {0}", type="INTEGER", value="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}}
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(value="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}}
            ),
        ),
        delete={"vendor_id": "TEST_VENDOR"},
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-products",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            attributes=Attributes(
                vendor_product_identifier="test_id {0}",
                vendor_product_description="test_desc",
            ),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}}
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(vendor_product_description="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}}
            ),
        ),
        delete={"vendor_id": "TEST_VENDOR"},
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-product-classes",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            attributes=Attributes(name="class {0}", rank=1),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}}
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(rank=2),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}}
            ),
        ),
        delete={"vendor_id": "TEST_VENDOR"},
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-pricing-classes",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            attributes=Attributes(name="class {0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}}
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(name="class {0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}}
            ),
        ),
        delete={"vendor_id": "TEST_VENDOR"},
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-customers",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            attributes=Attributes(name="customer {0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}}
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(name="customer {0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}}
            ),
        ),
        delete={"vendor_id": "TEST_VENDOR"},
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-quotes",
        status_codes=(ALL_ALLOWED, ALL_ALLOWED),
        post=Data(
            attributes=Attributes(vendor_quote_number="quote {0}", status="active"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_customers={
                    "data": {
                        "id": TEST_VENDOR_CUSTOMER_1_ID,
                        "type": "vendor-customers",
                    }
                },
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(status="rejected"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_customers={
                    "data": {
                        "id": TEST_VENDOR_CUSTOMER_1_ID,
                        "type": "vendor-customers",
                    }
                },
            ),
        ),
        delete=dict(
            vendor_id="TEST_VENDOR", vendor_customer_id=TEST_VENDOR_CUSTOMER_1_ID
        ),
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-quotes-attrs",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            attributes=Attributes(attr="test_attr {0}", type="INTEGER", value="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_quotes={
                    "data": {"id": TEST_VENDOR_QUOTE_ID, "type": "vendor-quotes"}
                },
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(value="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_quotes={
                    "data": {"id": TEST_VENDOR_QUOTE_ID, "type": "vendor-quotes"}
                },
            ),
        ),
        delete=dict(vendor_id="TEST_VENDOR", vendor_quotes_id=TEST_VENDOR_QUOTE_ID),
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-quote-products",
        status_codes=(ALL_ALLOWED, SCA_ONLY),
        post=Data(
            attributes=Attributes(tag="test_product {0}", qty="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_quotes={
                    "data": {"id": TEST_VENDOR_QUOTE_ID, "type": "vendor-quotes"}
                },
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(qty="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_quotes={
                    "data": {"id": TEST_VENDOR_QUOTE_ID, "type": "vendor-quotes"}
                },
            ),
        ),
        delete=dict(vendor_id="TEST_VENDOR", vendor_quotes_id=TEST_VENDOR_QUOTE_ID),
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-product-to-class-mapping",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_products={
                    "data": {"id": int(TEST_VENDOR_PRODUCT), "type": "vendor-products"}
                },
                vendor_product_classes={
                    "data": {
                        "id": int(TEST_VENDOR_PRODUCT_CLASS),
                        "type": "vendor-product-classes",
                    }
                },
            ),
        ),
        delete=dict(vendor_id="TEST_VENDOR", vendor_product_id=TEST_VENDOR_PRODUCT),
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-product-class-discounts",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            attributes=Attributes(discount="{0}", effective_date=str(FUTURE_DATE)),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_customers={
                    "data": {
                        "id": int(TEST_VENDOR_CUSTOMER_1_ID),
                        "type": "vendor-customers",
                    }
                },
                vendor_product_classes={
                    "data": {
                        "id": int(TEST_VENDOR_PRODUCT_CLASS),
                        "type": "vendor-product-classes",
                    }
                },
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(discount="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_customers={
                    "data": {
                        "id": int(TEST_VENDOR_CUSTOMER_1_ID),
                        "type": "vendor-customers",
                    }
                },
                vendor_product_classes={
                    "data": {
                        "id": int(TEST_VENDOR_PRODUCT_CLASS),
                        "type": "vendor-product-classes",
                    }
                },
            ),
        ),
        delete=dict(
            vendor_id="TEST_VENDOR", vendor_customer_id=TEST_VENDOR_CUSTOMER_1_ID
        ),
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-product-attrs",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            attributes=Attributes(attr="attr {0}", type="INTEGER", value="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_products={
                    "data": {
                        "id": int(TEST_VENDOR_PRODUCT),
                        "type": "vendor-products",
                    }
                },
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(value="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_products={
                    "data": {
                        "id": int(TEST_VENDOR_PRODUCT),
                        "type": "vendor-products",
                    }
                },
            ),
        ),
        delete=dict(vendor_id="TEST_VENDOR", vendor_product_id=TEST_VENDOR_PRODUCT),
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-pricing-by-customer",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            attributes=Attributes(
                use_as_override=False, price="{0}", effective_date=str(FUTURE_DATE)
            ),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_customers={
                    "data": {
                        "id": int(TEST_VENDOR_CUSTOMER_1_ID),
                        "type": "vendor-customers",
                    }
                },
                vendor_products={
                    "data": {
                        "id": int(TEST_VENDOR_PRODUCT),
                        "type": "vendor-products",
                    }
                },
                vendor_pricing_classes={
                    "data": {
                        "id": int(TEST_VENDOR_PRICING_CLASS),
                        "type": "vendor-pricing-classes",
                    }
                },
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(use_as_override=True),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_customers={
                    "data": {
                        "id": int(TEST_VENDOR_CUSTOMER_1_ID),
                        "type": "vendor-customers",
                    }
                },
            ),
        ),
        delete=dict(
            vendor_id="TEST_VENDOR", vendor_customer_id=TEST_VENDOR_CUSTOMER_1_ID
        ),
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-pricing-by-customer-attrs",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            attributes=Attributes(name="attr {0}", type="INTEGER", value="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_pricing_by_customer={
                    "data": {
                        "id": int(TEST_VENDOR_PRICING_BY_CUSTOMER),
                        "type": "vendor-pricing-by-customer",
                    }
                },
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(value="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_pricing_by_customer={
                    "data": {
                        "id": int(TEST_VENDOR_PRICING_BY_CUSTOMER),
                        "type": "vendor-pricing-by-customer",
                    }
                },
            ),
        ),
        delete=dict(
            vendor_id="TEST_VENDOR",
            vendor_pricing_by_customer_id=str(TEST_VENDOR_PRICING_BY_CUSTOMER),
        ),
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-pricing-by-class",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            attributes=Attributes(price="{0}", effective_date=str(datetime.today())),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_pricing_classes={
                    "data": {
                        "id": int(TEST_VENDOR_PRICING_CLASS),
                        "type": "vendor-pricing-classes",
                    }
                },
                vendor_products={
                    "data": {
                        "id": int(TEST_VENDOR_PRODUCT),
                        "type": "vendor-products",
                    }
                },
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(price="{0}", effective_date=str(FUTURE_DATE)),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_pricing_classes={
                    "data": {
                        "id": int(TEST_VENDOR_PRICING_CLASS),
                        "type": "vendor-pricing-classes",
                    }
                },
            ),
        ),
        delete=dict(
            vendor_id="TEST_VENDOR",
            vendor_pricing_class_id=str(TEST_VENDOR_PRICING_CLASS),
        ),
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-customer-pricing-classes",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            attributes=Attributes(price="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_pricing_classes={
                    "data": {
                        "id": int(TEST_VENDOR_PRICING_CLASS),
                        "type": "vendor-pricing-classes",
                    }
                },
                vendor_customers={
                    "data": {
                        "id": int(TEST_VENDOR_CUSTOMER_1_ID),
                        "type": "vendor-customers",
                    }
                },
            ),
        ),
        delete=dict(
            vendor_id="TEST_VENDOR",
            vendor_customer_id=str(TEST_VENDOR_CUSTOMER_1_ID),
        ),
    ),
    Route(
        route=VENDORS_PREFIX / "vendor-customer-attrs",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            attributes=Attributes(name="attr {0}", type="INTEGER", value="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_customers={
                    "data": {
                        "id": int(TEST_VENDOR_CUSTOMER_1_ID),
                        "type": "vendor-customers",
                    }
                },
            ),
        ),
        patch=Data(
            id="{0}",
            attributes=Attributes(value="{0}"),
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_customers={
                    "data": {
                        "id": int(TEST_VENDOR_CUSTOMER_1_ID),
                        "type": "vendor-customers",
                    }
                },
            ),
        ),
        delete=dict(
            vendor_id="TEST_VENDOR",
            vendor_customer_id=str(TEST_VENDOR_CUSTOMER_1_ID),
        ),
    ),
    Route(
        route=VENDORS_PREFIX / "customer-pricing-by-customer",
        status_codes=(ALL_ALLOWED, ALL_ALLOWED),
        post=Data(
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                users={"data": {"id": int(TEST_USER_ID), "type": "users"}},
                vendor_pricing_by_customer={
                    "data": {
                        "id": int(TEST_VENDOR_PRICING_BY_CUSTOMER),
                        "type": "vendor-pricing-by-customer",
                    }
                },
            ),
        ),
        delete=dict(
            vendor_id="TEST_VENDOR",
            vendor_pricing_by_customer_id=str(TEST_VENDOR_PRICING_BY_CUSTOMER),
        ),
    ),
    Route(
        route=VENDORS_PREFIX / "customer-pricing-by-class",
        status_codes=(ALL_ALLOWED, ALL_ALLOWED),
        post=Data(
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                users={"data": {"id": int(TEST_USER_ID), "type": "users"}},
                vendor_pricing_by_class={
                    "data": {
                        "id": int(TEST_VENDOR_PRICING_BY_CLASS),
                        "type": "vendor-pricing-by-class",
                    }
                },
            ),
        ),
        delete=dict(
            vendor_id="TEST_VENDOR",
            vendor_pricing_by_class_id=str(TEST_VENDOR_PRICING_BY_CLASS),
        ),
    ),
    Route(
        route=VENDORS_PREFIX / "customer-location-mapping",
        status_codes=(SCA_ONLY, SCA_ONLY),
        post=Data(
            relationships=Relationships(
                vendors={"data": {"id": "TEST_VENDOR", "type": "vendors"}},
                vendor_customers={
                    "data": {
                        "id": int(TEST_VENDOR_CUSTOMER_1_ID),
                        "type": "vendor-customers",
                    }
                },
                customer_locations={
                    "data": {
                        "id": int(TEST_CUSTOMER_LOCATION),
                        "type": "customer-locations",
                    }
                },
            ),
        ),
        delete=dict(
            vendor_id="TEST_VENDOR", vendor_customer_id=TEST_VENDOR_CUSTOMER_1_ID
        ),
    ),
]


def post_patch_delete_params() -> tuple[str, list[Parameter]]:
    post_patch_delete_param_str = "perm,status_code,method,route,data"
    params: list[list[Parameter]] = [
        route.parameterize() for route in post_patch_delete_outline
    ]
    return post_patch_delete_param_str, chain(*params)


@mark.parametrize(*post_patch_delete_params())
def test_post_patch_delete(
    shared: Shared,
    perm: auth_overrides.Token,
    status_code: int,
    method: str,
    route: str,
    data: Union[Data, dict],
):
    """
    Patches and deletes shall be called only on objects created by POST requests within
    this test, albeit most records created will remain in the test DB soft-deleted.
    The `shared` fixture contains a dictionary used to pass id numbers created by
    post operations to patch and delete operations.

    Assert expected status codes by token type
        post - 200/401/501
        patch - 200/401/501
        delete - 204/401/501
    """
    app.dependency_overrides[authenticate_auth0_token] = perm
    client_method = getattr(test_client, method)
    match HTTPReqType(method):
        case HTTPReqType.POST:
            resp: Response = client_method(route, json=data.to_dict())
            assert resp.status_code == status_code, try_return_json(resp)
            if status_code < 400:
                shared.update((route, perm), resp.json()["data"]["id"])
        case HTTPReqType.PATCH:
            new_id = shared.get((route, perm))
            id_ = data.id.format(new_id) if new_id else 0
            try:
                id_ = int(id_)
            except:
                pass
            finally:
                data_updated: Data = replace(data, id=id_)
            route += f"/{id_}"
            resp: Response = client_method(route, json=data_updated.to_dict())
            if resp.status_code == 422:
                route = route[:-1] + "a"
                data_updated: Data = replace(data, id="a")
                resp = client_method(route, json=data_updated.to_dict())
            assert resp.status_code == status_code, try_return_json(resp)
        case HTTPReqType.DELETE:
            new_id = shared.get((route, perm))
            if not new_id:
                new_id = 0
            route += f"/{new_id}"
            if data:
                queries = [f"{k}={v}" for k, v in data.items()]
                query = "?" + "&".join(queries)
            else:
                query = ""
            route += query
            resp: Response = client_method(route)
            if resp.status_code == 422:
                route = route[:-1] + "a"
                resp = client_method(route)
            if 199 < status_code < 300:
                status_code = 204
            assert resp.status_code == status_code, try_return_json(resp)


filter_name_to_none = "filter_vendor_product_classes__name=SomeName"
filter_name_success = "filter_vendor_product_classes__name=Accessory"
filter_rank_success = "filter_vendor_product_classes__rank=1"
filter_name_and_rank_success = "filter_vendor_product_classes__name=Accessory&filter_vendor_product_classes__rank=1"
filter_name_and_rank_none = "filter_vendor_product_classes__name=Accessory&filter_vendor_product_classes__rank=2"
no_filter = ""
filters = [
    (filter_name_to_none, 0),
    (filter_name_success, 1),
    (filter_rank_success, 1),
    (filter_name_and_rank_success, 1),
    (filter_name_and_rank_none, 0),
    (no_filter, 12),
]


@mark.parametrize("filter_arg,item_count", filters)
def test_deep_filtering_within_includes(filter_arg: str, item_count: int):
    app.dependency_overrides[authenticate_auth0_token] = auth_overrides.AdminToken
    base_route = str(TEST_VENDOR_TEST_CUSTOMER)
    route_with_includes = (
        base_route + "?include="
        "vendor-pricing-by-customer.vendor-products.vendor-product-attrs,"
        "vendor-pricing-by-customer.vendor-products.vendor-product-to-class-mapping"
        ".vendor-product-classes"
    )
    full_route = route_with_includes + f"&{filter_arg}"
    resp = test_client.get(full_route)
    assert resp.status_code == 200, resp.text
    included = resp.json()["included"]
    the_count = 0
    for include in included:
        if include["type"] == "vendor-products":
            the_count += 1
    assert the_count == item_count
