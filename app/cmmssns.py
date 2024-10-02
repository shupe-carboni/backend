from os import getenv
from time import sleep
from dataclasses import dataclass
from requests import post

CMMSSNS_URL: str = getenv("CMMSSNS_AUDIENCE")


@dataclass
class CMMSSNSToken:
    value: str = ""

    @classmethod
    def get_token(cls, retry: int = 0) -> None:
        if retry > 2:
            raise Exception("Unable to obtain auth token from CMMSSNS API")
        if retry:
            sleep(retry)
        CMMSSNS_AUTH0 = getenv("CMMSSNS_AUTH0_DOMAIN")
        payload = {
            "client_id": getenv("CMMSSNS_CLIENT_ID"),
            "client_secret": getenv("CMMSSNS_CLIENT_SECRET"),
            "audience": CMMSSNS_URL,
            "grant_type": getenv("CMMSSNS_GRANT_TYPE"),
        }
        resp = post(CMMSSNS_AUTH0 + "/oauth/token", json=payload)
        if resp.status_code == 200:
            resp_body = resp.json()
            token_type = resp_body["token_type"]
            access_token = resp_body["access_token"]
            cls.value = f"{token_type} {access_token}"
        else:
            retry += 1
            cls.get_token(retry=retry)

    @classmethod
    def auth_header(cls) -> dict[str, str]:
        if not cls.value:
            cls.get_token()
        return {"Authorization": cls.value}
