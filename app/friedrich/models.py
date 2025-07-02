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

import requests
import re
from datetime import date, datetime
from pydantic import BaseModel, field_validator
from enum import StrEnum, auto
from os import getenv
from random import randint
from bs4 import BeautifulSoup as bs
from app.version import VERSION


Cookies = dict[str, str]


class QuoteStatus(StrEnum):
    APPROVED = auto()
    DENIED = auto()
    PENDING = auto()
    NEAR_EXPIRED = auto()
    EXPIRED = auto()


STATUS_MAPPING = {
    "Approved": QuoteStatus.APPROVED,
    "Pending Approval": QuoteStatus.PENDING,
    "Approved - About to Expire": QuoteStatus.NEAR_EXPIRED,
}


class QuoteProjectContacts(BaseModel):
    contact_name: str
    contact_email: str
    submitter_name: str
    submitter_email: str


class QuoteProjectDetails(BaseModel):
    market_type: str
    city: str
    state: str


class Quote(BaseModel):
    guid: str
    quote_name: str
    account_name: str
    approval_status: QuoteStatus
    quote_number: int
    created_date: date
    expiration_date: date
    project_details: QuoteProjectDetails
    project_contacts: QuoteProjectContacts

    @field_validator("created_date", "expiration_date", mode="before")
    @classmethod
    def parse_date(cls, value: str) -> date:
        try:
            return datetime.strptime(value, "%B %d, %Y").date()
        except ValueError as e:
            raise ValueError(
                f"Invalid date format for {value}. Expected Month DD, YYYY"
            ) from e

    @field_validator("approval_status", mode="before")
    @classmethod
    def map_status(cls, value: str) -> QuoteStatus:
        try:
            return STATUS_MAPPING[value]
        except KeyError as e:
            raise KeyError(
                f"Status unmapped for {value}. "
                f"Expected one of the following: {[s for s in QuoteStatus.__members__]}"
            ) from e


class Action:
    """Base Class for URL-based request actions that simplifies link building and uses
    a requests session to make requests with a custom User Agent set on every request"""

    __cookies: Cookies = dict()

    def __init__(self, req_session: requests.Session) -> None:
        self.domain: str = getenv("FRIEDRICH_QUOTE_PORTAL_DOMAIN")
        self.contact_id: str = getenv("FRIEDRICH_CONTACT_ID")
        self.req_session = req_session

        self.path: str
        self.params: dict[str, str | int]
        self.resp: bs = None
        self.resp_raw: requests.Response = None

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

    def make_request(self) -> "Action":
        user_agent = getenv("CUSTOM_USER_AGENT").format(version=VERSION)
        custom_headers = {
            "User-Agent": user_agent,
        }
        self.req_session.headers.update(custom_headers)
        if cookies := Action._cookies():
            self.req_session.cookies = cookies
        resp = self.req_session.get(url=str(self))
        if resp.status_code == 302:
            # session expiry responds with a redirect to the dashboard for login
            # login again (re-setting shared cookies) and retry the request
            if isinstance(self, Login):
                raise Exception(
                    "Login Request may have failed. Login attempt returned 302."
                )
            Login().make_request()
            return self.make_request()
        Action._cookies(new_cookies=resp.cookies)
        self.resp = bs(resp.text, "html.parser")
        self.resp_raw = resp
        return self

    def format_resp(self) -> BaseModel | list[BaseModel] | str:
        """implemeted by subclass"""
        ...


class Login(Action):
    def __init__(self, req_session: requests.Session) -> None:
        super().__init__(req_session)
        self.path: str = "Ajax_ValidateSignOn.aspx"
        self.params = {
            "EmailAddress": getenv("FRIEDRICH_LOGIN_NAME"),
            "Password": getenv("FRIEDRICH_LOGIN_PASSWORD"),
        }


class GetQuotes(Action):
    def __init__(self, req_session: requests.Session) -> None:
        super().__init__(req_session)
        self.path: str = "Ajax_DashboardV2_LoadQuotes.aspx"
        self.params = {"ContactID": self.contact_id}

    def format_resp(self) -> list[Quote]:
        if not self.resp:
            raise Exception("No request made or the request call failed")

        quotes = []
        gridrow_classes = [
            f"gridrow_{status}" for status in QuoteStatus.__members__.values()
        ]
        grid_rows = self.resp.find_all("td", class_=gridrow_classes)

        # The following loop was auto-generated feeding the raw HTML to Grok 3
        for i, row in enumerate(grid_rows):
            print(f"processing quote {i+1} of {len(grid_rows)}")
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

            # make another request for the project details
            project_details = (
                GetQuoteProjectDetails(self.req_session, guid)
                .make_request()
                .format_resp()
            )
            contact_info = (
                GetQuoteContacts(self.req_session, guid).make_request().format_resp()
            )

            try:
                quote = Quote(
                    guid=guid,
                    quote_name=quote_name,
                    account_name=account_name,
                    approval_status=approval_status,
                    quote_number=quote_number,
                    created_date=created_date,
                    expiration_date=expires_date,
                    project_details=project_details,
                    project_contacts=contact_info,
                )
            except Exception as e:
                print("--- quote ---")
                print(e)
                print("\t", guid)
                print("\t", quote_name)
                print("\t", account_name)
                print("\t", approval_status)
                print("\t", quote_number)
                print("\t", created_date)
                print("\t", expires_date)
            else:
                quotes.append(quote)
        return quotes


class GetQuoteOpportunityInfo(Action):
    def __init__(self, req_session: requests.Session, quote_id) -> None:
        super().__init__(req_session)
        self.path: str = "Ajax_CreateQuoteLoadSelectedQuote.aspx"
        self.params = {"QuoteID": quote_id}

    def format_resp(self) -> str:
        opportunity_id = self.resp_raw.text.split("^")[0]
        return opportunity_id


class GetQuoteContacts(Action):
    def __init__(self, req_session: requests.Session, quote_id) -> None:
        super().__init__(req_session)
        self.path: str = "CreateNewQuote.aspx"
        self.params = {"QuoteID": quote_id}

    def format_resp(self) -> QuoteProjectContacts:
        project_section = self.resp.find("span", id="spanProjects")
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


class GetQuoteProjectDetails(Action):
    def __init__(self, req_session: requests.Session, quote_id) -> None:
        super().__init__(req_session)
        self.path: str = "Ajax_CreateQuoteLoadSelectedProject.aspx"
        opp_id = (
            GetQuoteOpportunityInfo(req_session, quote_id).make_request().format_resp()
        )
        self.params = {"OpportunityID": opp_id}

    def format_resp(self) -> QuoteProjectDetails:
        """
        //do processing of incoming data
            var ajaxResponse = xmlHttp.responseText;
            var arrResponse = ajaxResponse.split("^");

        //set form values
            document.getElementById("OpportunityID").value = arrResponse[0];
            document.getElementById("spnProjectTitle").innerHTML = arrResponse[2];

        //need to split out arrResponse[2] amongst the 3 fields
            var oppNameSplit = arrResponse[2].split(" - ");
            document.getElementById("OpportunityName").value = oppNameSplit[0];

            var oppNameSplit2 = oppNameSplit[1].split(", ");
            document.getElementById("OpportunityCity").value = oppNameSplit2[0];
            document.getElementById("OpportunityState").value = oppNameSplit2[1];

            adjustStateFields();

            document.getElementById("MarketType").value = arrResponse[29];
            document.getElementById("QuotingTo").value = arrResponse[30];

            document.getElementById("AccountChanged").value = "false";
            document.getElementById("OpportunityChanged").value = "false";
        """
        if not self.resp:
            raise Exception("No request made or the request call failed")

        try:
            resp_arr = self.resp_raw.text.split("^")
            """
            BUG Frierich allows hypens in the project name
                As such the following approach will fail on unpacking the second split
                if the project name contains a hyphen.

            city, state = resp_arr[2].split(" - ")[1].split(", ")

            """
            city, state = resp_arr[2].split(" - ")[-1].split(", ")
            market_type = resp_arr[29]
        except Exception as e:
            for i, arr_e in enumerate(resp_arr):
                print(i, "\t", arr_e)
            raise e

        return QuoteProjectDetails(
            market_type=market_type,
            city=city,
            state=state,
        )
