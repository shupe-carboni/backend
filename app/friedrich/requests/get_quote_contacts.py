import aiohttp
import asyncio
from functools import partial
from bs4 import BeautifulSoup as bs

from app.friedrich.models import QuoteProjectContacts
from app.friedrich.requests.action_base import Action


class GetQuoteContacts(Action):
    def __init__(self, req_session: aiohttp.ClientSession, quote_id) -> None:
        super().__init__(req_session)
        self.path: str = "CreateNewQuote.aspx"
        self.quote_id = quote_id
        self.params = {"QuoteID": quote_id}
        self.contacts: QuoteProjectContacts = None
        self.project_account_id: str

    async def chain(self) -> "GetQuoteContacts":
        await self.make_request()
        await self.format_resp()
        return self

    @staticmethod
    def parse_resp(resp: bs) -> tuple[QuoteProjectContacts, str]:
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
        # unrelated to contact info but this needs to be grabbed here
        project_account_id = (
            project_section.find("input", id="ProjectAccount")["value"]
            if project_section and project_section.find("input", id="ProjectAccount")
            else ""
        )

        return (
            QuoteProjectContacts(
                contact_name=contact_name,
                contact_email=contact_email,
                submitter_name=submitter_name,
                submitter_email=submitter_email,
            ),
            project_account_id,
        )

    async def format_resp(self) -> None:
        parsing = partial(self.parse_resp, self.resp)
        self.contacts, self.project_account_id = (
            await asyncio.get_running_loop().run_in_executor(None, parsing)
        )
        return

    def ret(self) -> QuoteProjectContacts:
        return self.contacts
