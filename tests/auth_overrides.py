from app.auth import Permissions
from dotenv import load_dotenv
from app.customers.models import NewCMMSSNSCustomer, CMMSSNSCustomerResp

load_dotenv()
from os import getenv
from random import randint


class Token:
    permissions: Permissions
    email_verified: bool
    email: str


class AdminToken(Token):
    permissions = Permissions.sca_admin
    email_verified = True
    email = getenv("TEST_USER_EMAIL")


class SCAEmployeeToken(Token):
    permissions = Permissions.sca_employee
    email_verified = True
    email = getenv("TEST_USER_EMAIL")


class DeveloperToken(Token):
    permissions = Permissions.developer
    email_verified = True
    email = getenv("TEST_USER_EMAIL")


class CustomerAdminToken(Token):
    permissions = Permissions.customer_admin
    email_verified = True
    email = getenv("TEST_USER_EMAIL")


class CustomerManagerToken(Token):
    permissions = Permissions.customer_manager
    email_verified = True
    email = getenv("TEST_USER_EMAIL")


class CustomerStandardToken(Token):
    permissions = Permissions.customer_std
    email_verified = True
    email = getenv("TEST_USER_EMAIL")


def mock_new_cmmssns_customer(new_customer: NewCMMSSNSCustomer) -> CMMSSNSCustomerResp:
    return CMMSSNSCustomerResp(
        jsonapi={"version": "123.456"},
        meta={"client": "test"},
        included=[],
        data={
            "id": randint(1000000, 9999999),
            "type": "customers",
            "attributes": {"name": new_customer.data.attributes.name},
        },
    )


def mock_get_mock_new_cmmssns_customer():
    return mock_new_cmmssns_customer
