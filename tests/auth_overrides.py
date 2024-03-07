from functools import partial
from app.auth import Permissions, perm_category_present
from dotenv import load_dotenv; load_dotenv()
from os import getenv

class AdminToken:
    permissions = {perm.name: perm.value.sca_admin for perm in Permissions}
    email_verified = True
    def perm_level(category):
        return Permissions[category].value.sca_admin.value

class SCAEmployeeToken:
    permissions = {perm.name: perm.value.sca_employee for perm in Permissions}
    email_verified = True
    def perm_level(category):
        return Permissions[category].value.sca_employee.value

class CustomerAdminToken:
    permissions = {perm.name: perm.value.customer_admin for perm in Permissions}
    email_verified = True
    def perm_level(category):
        return Permissions[category].value.customer_admin.value

class CustomerManagerToken:
    permissions = {perm.name: perm.value.customer_manager for perm in Permissions}
    email_verified = True
    def perm_level(category):
        return Permissions[category].value.customer_manager.value

class CustomerStandardToken:
    permissions = {perm.name: perm.value.customer_std for perm in Permissions}
    email_verified = True
    email = getenv('ADMIN_EMAIL')
    def perm_level(category):
        return Permissions[category].value.customer_std.value

def auth_as_sca_admin(perm_category):
    return partial(perm_category_present, AdminToken, perm_category)

def auth_as_sca_employee(perm_category):
    return partial(perm_category_present, SCAEmployeeToken, perm_category)

def auth_as_customer_admin(perm_category):
    return partial(perm_category_present, CustomerAdminToken, perm_category)

def auth_as_customer_manager(perm_category):
    return partial(perm_category_present, CustomerManagerToken, perm_category)

def auth_as_customer_std(perm_category):
    return partial(perm_category_present, CustomerStandardToken, perm_category)


