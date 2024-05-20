from app.auth import Permissions
from dotenv import load_dotenv

load_dotenv()
from os import getenv


class AdminToken:
    permissions = Permissions.sca_admin
    email_verified = True


class SCAEmployeeToken:
    permissions = Permissions.sca_employee
    email_verified = True


class DeveloperToken:
    permissions = Permissions.developer
    email_verified = True
    email = getenv("TEST_USER_EMAIL")


class CustomerAdminToken:
    permissions = Permissions.customer_admin
    email_verified = True
    email = getenv("TEST_USER_EMAIL")


class CustomerManagerToken:
    permissions = Permissions.customer_manager
    email_verified = True
    email = getenv("TEST_USER_EMAIL")


class CustomerStandardToken:
    permissions = Permissions.customer_std
    email_verified = True
    email = getenv("TEST_USER_EMAIL")
