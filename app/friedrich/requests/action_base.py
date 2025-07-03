import aiohttp
from os import getenv
from random import randint
from pydantic import BaseModel
from bs4 import BeautifulSoup as bs

from app.version import VERSION

Cookies = dict[str, str]


class Action:
    """Base Class for URL-based request actions that simplifies link building and uses
    a requests session to make requests with a custom User Agent set on every request"""

    __cookies: Cookies = dict()

    def __init__(self, req_session: aiohttp.ClientSession) -> None:
        self.domain: str = getenv("FRIEDRICH_QUOTE_PORTAL_DOMAIN")
        self.contact_id: str = getenv("FRIEDRICH_CONTACT_ID")
        self.req_session = req_session

        self.path: str
        self.params: dict[str, str | int]
        self.resp: bs = None
        self.resp_raw: str = None

    @staticmethod
    def _gen_cache() -> int:
        """mirrors how the portal sets the cache number for its requests"""
        return randint(0, 99999)

    @classmethod
    def _cookies(cls, new_cookies: Cookies = None) -> Cookies:
        """persist cookies between request sessions by get/set-ing the Class variable"""
        if new_cookies:
            cls.__cookies = new_cookies
        return cls.__cookies

    def __str__(self) -> str:
        """build the url with parameters"""
        params = self.params
        params["Cache"] = self._gen_cache()
        endpoint = self.domain + self.path
        built = f"{endpoint}?{'&'.join([f'{k}={v}' for k,v in params.items()])}"
        return built

    async def make_request(self) -> "Action":
        user_agent = getenv("CUSTOM_USER_AGENT").format(version=VERSION)
        custom_headers = {
            "User-Agent": user_agent,
        }
        self.req_session.headers.update(custom_headers)
        if cookies := Action._cookies():
            if cookies != self.req_session.cookie_jar:
                self.req_session.cookie_jar.update_cookies(cookies)
        resp = await self.req_session.get(url=str(self))
        if resp.status == 302:
            # session expiry responds with a redirect to the dashboard for login
            # login again (re-setting shared cookies) and retry the request
            if isinstance(self, Login):
                raise Exception(
                    "Login Request may have failed. Login attempt returned 302."
                )
            await Login().make_request()
            return await self.make_request()
        Action._cookies(new_cookies=resp.cookies)
        resp_text = await resp.text()
        self.resp = bs(resp_text, "html.parser")
        self.resp_raw = resp_text
        return self

    def format_resp(self) -> "Action":
        """implemeted by subclass"""

    def ret(self) -> BaseModel | list[BaseModel] | str:
        """implemeted by subclass"""


class Login(Action):
    def __init__(self, req_session: aiohttp.ClientSession) -> None:
        super().__init__(req_session)
        self.path: str = "Ajax_ValidateSignOn.aspx"
        self.params = {
            "EmailAddress": getenv("FRIEDRICH_LOGIN_NAME"),
            "Password": getenv("FRIEDRICH_LOGIN_PASSWORD"),
        }
