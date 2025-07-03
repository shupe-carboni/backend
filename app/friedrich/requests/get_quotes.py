import re
import aiohttp
import asyncio
from time import time
from logging import getLogger

from app.friedrich.models import (
    QuoteProjectInitalDetails,
    Quote,
    QuoteProjectAttributes,
    QuoteProjectContacts,
)
from app.friedrich.models import QuoteStatus
from app.friedrich.requests.action_base import Action
from app.friedrich.requests.get_quote_project_details import GetQuoteProjectDetails
from app.friedrich.requests.get_quote_contacts import GetQuoteContacts
from app.friedrich.requests.get_quote_products import GetQuoteProductLineItems

logger = getLogger("uvicorn.info")


class GetQuotes(Action):
    def __init__(self, req_session: aiohttp.ClientSession) -> None:
        super().__init__(req_session)
        self.path: str = "Ajax_DashboardV2_LoadQuotes.aspx"
        self.params = {"ContactID": self.contact_id}
        self.quotes: list[Quote] | list[QuoteProjectInitalDetails] = None
        logger.info(f"Friedrich Quote fetching initialized")

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

            products = await GetQuoteProductLineItems(
                self.req_session,
                project_account_id=contact_info.project_account_id,
                quote_id=guid,
                opp_id=addnl_project_details.opp_info.opp_id,
                zip_code=addnl_project_details.opp_info.zip_code,
                tax_exempt=addnl_project_details.opp_info.tax_exempt,
                price_id=addnl_project_details.opp_info.price_level_id,
                quote_shipments=addnl_project_details.opp_info.quote_shipments,
                quote_notes=addnl_project_details.opp_info.quote_shipments,
            ).chain()
            products_data = products.ret()

            logger.info(f"({time()}) Quote: {guid} - done")
            return Quote(
                guid=guid,
                quote_attributes=QuoteProjectAttributes(
                    **quote.model_dump(),
                    **addnl_project_details_data.model_dump(),
                ),
                quote_contacts=contact_info_data,
                quote_products=products_data,
            )

        # async iteration over quotes for additional requests filling details
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
