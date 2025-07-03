"""
* Ajax_ValidateSignOn.aspx -- authentication
    * if the cookie is stored and still valid, potentially avoidable for most syncs
* Ajax_DashboardV2_LoadQuotes.aspx -- list of quotes
* CreateNewQuote.aspx -- Quote Contact Info in the HTML
* Ajax_CreateQuoteLoadSelectedQuote.aspx -- get an opportunity ID from raw response
* Ajax_CreateQuoteLoadSelectedProject.aspx -- get additional project details
    using opportunity ID
* Ajax_CreateQuoteManageLineItems.aspx -- quote line items

Capturing data will require various combinations of query parameters in GET requests
and parsing of HTML responses to the simulated AJAX calls
"""

import aiohttp
import re
import asyncio
from functools import partial
from time import time
from pydantic import BaseModel
from os import getenv
from random import randint
from bs4 import BeautifulSoup as bs
from app.version import VERSION
from app.friedrich.models import *
from logging import getLogger

logger = getLogger("uvicorn.info")
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


class GetQuotes(Action):
    def __init__(self, req_session: aiohttp.ClientSession) -> None:
        super().__init__(req_session)
        self.path: str = "Ajax_DashboardV2_LoadQuotes.aspx"
        self.params = {"ContactID": self.contact_id}
        self.quotes: list[Quote] | list[QuoteProjectInitalDetails] = None

    async def collect_addnl_details(self) -> "GetQuotes":
        if not self.quotes:
            raise Exception(
                "Run `make_request()` and `format_resp()` before this operation"
            )

        async def fetch_addnl_details(quote: QuoteProjectInitalDetails) -> Quote:
            guid = quote.guid
            # set up tasks
            # additional attributes
            addnl_project_details_task = GetQuoteProjectDetails(
                self.req_session, guid
            ).make_request()
            # contacts
            contact_info_task = GetQuoteContacts(self.req_session, guid).chain()

            # execute async tasks
            addnl_project_details: GetQuoteProjectDetails
            contact_info: GetQuoteContacts
            addnl_project_details, contact_info = await asyncio.gather(
                addnl_project_details_task, contact_info_task
            )
            addnl_project_details_data = addnl_project_details.format_resp().ret()
            contact_info_data = contact_info.ret()

            # TODO retrieve product line items - this will be a long response time
            # because the server just seems to take a long time to respond to this
            # particular request
            logger.info(f"({time()}) Quote: {guid} - done")
            return Quote(
                guid=guid,
                quote_attributes=QuoteProjectAttributes(
                    **quote.model_dump(), **addnl_project_details_data.model_dump()
                ),
                quote_contacts=QuoteProjectContacts(**contact_info_data.model_dump()),
            )

        # async iteration over quotes for additional requests filling details
        logger.info(f"({time()}) Quote additional details fetching loop")
        full_quotes = await asyncio.gather(
            *(fetch_addnl_details(quote) for quote in self.quotes)
        )
        self.quotes = list(full_quotes)
        return self

    def format_resp(self) -> "GetQuotes":
        if not self.resp:
            raise Exception("No request made or the request call failed")

        quotes = []
        gridrow_classes = [
            f"gridrow_{status}" for status in QuoteStatus.__members__.values()
        ]
        grid_rows = self.resp.find_all("td", class_=gridrow_classes)

        # The following loop was auto-generated feeding the raw HTML to Grok 3
        for row in grid_rows:
            # Extract GUID from viewQuote or extendOptions onclick attribute
            td = row.find(
                "td", onclick=re.compile(r'(viewQuote|extendOptions)\("([^"]+)"')
            )
            if not td:
                continue
            onclick = td.get("onclick")
            guid_match: re.Match = re.search(r'"([0-9a-f-]{36})"', onclick)
            if not guid_match:
                continue
            guid = guid_match.group(1)

            # First table: quote name, approval status, quote number
            first_table = td.find("table")
            if not first_table:
                continue
            first_row = first_table.find("tr")
            if not first_row:
                continue
            cells = first_row.find_all("td")
            if len(cells) != 3:
                continue

            # Quote name
            quote_name = (
                cells[0].find("b").get_text(strip=True) if cells[0].find("b") else ""
            )

            # Approval status
            approval_cell = cells[1].find("b")
            approval_status = ""
            if approval_cell:
                approval_fonts = approval_cell.find_all("font")
                approval_status = " ".join(
                    font.get_text(strip=True) for font in approval_fonts
                )

            # Quote number
            quote_number = (
                cells[2].find("b").get_text(strip=True) if cells[2].find("b") else ""
            )

            # Second table: project name, created date, expires date
            second_table = (
                td.find_all("table")[1] if len(td.find_all("table")) > 1 else None
            )
            if not second_table:
                continue
            second_rows = second_table.find_all("tr")
            if len(second_rows) < 2:
                continue

            # First row of second table: project name, created date
            second_table_first_row_cells = second_rows[0].find_all("td")
            # Account name is in the first cell of the first row of the second table
            account_name = (
                second_table_first_row_cells[1].find("b").get_text(strip=True)
                if len(second_table_first_row_cells) > 1
                and second_table_first_row_cells[1]
                .get_text(strip=True)
                .startswith("Account:")
                and second_table_first_row_cells[1].find("b")
                else None
            )
            created_date = (
                second_table_first_row_cells[2].find("b").get_text(strip=True)
                if len(second_table_first_row_cells) > 2
                and second_table_first_row_cells[2].find("b")
                else ""
            )

            # Second row of second table: expires date
            second_row_cells = second_rows[1].find_all("td")
            expires_date = (
                second_row_cells[1].find("b").get_text(strip=True)
                if len(second_row_cells) > 1 and second_row_cells[1].find("b")
                else ""
            )

            try:
                quote = QuoteProjectInitalDetails(
                    guid=guid,
                    quote_name=quote_name,
                    account_name=account_name,
                    approval_status=approval_status,
                    quote_number=quote_number,
                    created_date=created_date,
                    expiration_date=expires_date,
                )
            except Exception as e:
                print("--- quote ---")
                print(e)
            else:
                quotes.append(quote)
        self.quotes = quotes
        return self

    def ret(self) -> list[Quote]:
        return self.quotes


class GetQuoteOpportunityInfo(Action):
    def __init__(self, req_session: aiohttp.ClientSession, quote_id) -> None:
        super().__init__(req_session)
        self.path: str = "Ajax_CreateQuoteLoadSelectedQuote.aspx"
        self.quote_id = quote_id
        self.params = {"QuoteID": quote_id}
        self.opp_id = None

    def format_resp(self) -> "GetQuoteOpportunityInfo":
        opportunity_id = self.resp_raw.split("^")[0]
        self.opp_id = opportunity_id
        return self

    def ret(self) -> str:
        return self.opp_id


class GetQuoteContacts(Action):
    def __init__(self, req_session: aiohttp.ClientSession, quote_id) -> None:
        super().__init__(req_session)
        self.path: str = "CreateNewQuote.aspx"
        self.quote_id = quote_id
        self.params = {"QuoteID": quote_id}
        self.contacts = None

    async def chain(self) -> "GetQuoteContacts":
        await self.make_request()
        await self.format_resp()
        return self

    @staticmethod
    def parse_resp(resp: bs):
        project_section = resp.find("span", id="spanProjects")
        contact_name = (
            project_section.find("input", id="QuoContactName")["value"]
            if project_section and project_section.find("input", id="QuoContactName")
            else ""
        )
        contact_email = (
            project_section.find("input", id="QuoContactEmail")["value"]
            if project_section and project_section.find("input", id="QuoContactEmail")
            else ""
        )
        submitter_name = (
            project_section.find("input", id="SubmitByName")["value"]
            if project_section and project_section.find("input", id="SubmitByName")
            else ""
        )
        submitter_email = (
            project_section.find("input", id="SubmitByEmail")["value"]
            if project_section and project_section.find("input", id="SubmitByEmail")
            else ""
        )

        return QuoteProjectContacts(
            contact_name=contact_name,
            contact_email=contact_email,
            submitter_name=submitter_name,
            submitter_email=submitter_email,
        )

    async def format_resp(self) -> None:
        parsing = partial(self.parse_resp, self.resp)
        self.contacts = await asyncio.get_running_loop().run_in_executor(None, parsing)
        return

    def ret(self) -> QuoteProjectContacts:
        return self.contacts


class GetQuoteProjectDetails(Action):
    def __init__(self, req_session: aiohttp.ClientSession, quote_id) -> None:
        super().__init__(req_session)
        self.path: str = "Ajax_CreateQuoteLoadSelectedProject.aspx"
        self.details = None
        self.quote_id = quote_id
        self.params = {}

    async def make_request(self):
        opp_id = await GetQuoteOpportunityInfo(
            self.req_session, self.quote_id
        ).make_request()
        self.params.update({"OpportunityID": opp_id.format_resp().ret()})
        return await super().make_request()

    def format_resp(self) -> "GetQuoteProjectDetails":
        """
        JS from the portal that processes the carrot-delimited text response
        adding my own comments with `<!-- -->`
        ```javascript
        //do processing of incoming data
            var ajaxResponse = xmlHttp.responseText;
            var arrResponse = ajaxResponse.split("^");

        //need to split out arrResponse[2] amongst the 3 fields
            <!-- opp name - location -->
            var oppNameSplit = arrResponse[2].split(" - ");
            <!-- city, state -->
            var oppNameSplit2 = oppNameSplit[1].split(", ");
            <!-- set values by position -->
            document.getElementById("OpportunityCity").value = oppNameSplit2[0];
            document.getElementById("OpportunityState").value = oppNameSplit2[1];
            document.getElementById("MarketType").value = arrResponse[29];
            document.getElementById("QuotingTo").value = arrResponse[30];
        ```
        BUG Frierich allows hypens in the project name. This causes an error when
        the expectation is location data after the first hyphen. Since the expectation
        is a length 2 array, I use negative index (-1) instead of the second index (1)
        """
        if not self.resp:
            raise Exception("No request made or the request call failed")

        try:
            resp_arr = self.resp_raw.split("^")
            city, state = resp_arr[2].split(" - ")[-1].split(", ")
            market_type = resp_arr[29]
        except Exception as e:
            for i, arr_e in enumerate(resp_arr):
                print(i, "\t", arr_e)
            raise e
        else:
            self.details = QuoteProjectAddnlDetails(
                market_type=market_type,
                city=city,
                state=state,
            )
        finally:
            return self

    def ret(self) -> QuoteProjectAddnlDetails:
        return self.details
