import re
import aiohttp
import asyncio
from logging import getLogger
from functools import partial
from pydantic import BaseModel
from bs4 import BeautifulSoup as bs

from app.friedrich.requests.action_base import Action
from app.friedrich.models import QuoteProduct

logger = getLogger("uvicorn.info")


class GetQuoteProductLineItems(Action):
    def __init__(
        self,
        req_session: aiohttp.ClientSession,
        project_account_id: str,
        quote_id: str,
        opp_id: str,
        zip_code: int,
        tax_exempt: bool,
        price_id: str,
        quote_shipments: int,
        quote_notes: str,
    ) -> None:
        super().__init__(req_session)
        self.path: str = "Ajax_CreateQuoteManageLineItems.aspx"
        self.quote_id = quote_id
        self.products = None
        self.params = {
            "ProjectAccountID": project_account_id,
            "QuoteID": quote_id,
            "OpportunityID": opp_id,
            "SplFileUpload1": None,
            "SplFileUpload2": None,
            "SplFileUpload3": None,
            "QuoteZipCode": zip_code,
            "QuoteTaxExempt": tax_exempt,
            "PriceLevelID": price_id,
            "LockFields": False,
            "CommissionRate": 0,
            "QuoteShipments": quote_shipments,
            "QuoteNotes": quote_notes,
            "LineItemID": 0,
            "ProductCommission": -1,
            "ProductID": 0,
            "Quantity": 0,
            "Discount": 0,
            "ToDo": "R",
        }

    @staticmethod
    def parse_data(resp: bs) -> list[QuoteProduct]:
        results = []
        main_table = resp.find("table", width="880")
        if not main_table:
            return results

        # Find all rows with class 'gridrowsmall' directly under the main table
        rows = main_table.find_all("td", class_="gridrowsmall")

        for row in rows:
            inner_table = row.find("table")
            if not inner_table:
                continue

            # Get all tds in the first tr of the inner table
            tds = inner_table.find("tr").find_all("td")
            if len(tds) < 3:
                continue

            # Product name (third td, contains sku)
            product_name = tds[2].get_text(strip=True).split("\n")[0]

            # Quantity (input value in ItemQty_X)
            qty_input = inner_table.find(
                "input", id=lambda x: x and x.startswith("ItemQty_")
            )
            qty = qty_input["value"] if qty_input else None

            # Unit price (input value in ItemPriceEach_X)
            price_input = inner_table.find(
                "input", id=lambda x: x and x.startswith("ItemPriceEach_")
            )
            unit_price = price_input["value"] if price_input else None
            if not unit_price:
                price_td = tds[7]  # After discount price each td
                unit_price = (
                    price_td.get_text(strip=True).split("\n")[0]
                    if price_td.get_text(strip=True)
                    else None
                )
            if unit_price:
                unit_price = float(re.sub(r"[^0-9.]", "", unit_price))

            result = QuoteProduct(
                product_name=product_name,
                quantity=qty,
                unit_price=unit_price,
            )
            results.append(result)
        return results

    async def format_resp(self) -> None:
        parsing = partial(self.parse_data, self.resp)
        self.products = await asyncio.get_running_loop().run_in_executor(None, parsing)
        return

    async def chain(self) -> "GetQuoteProductLineItems":
        await self.make_request()
        self.products = self.parse_data(self.resp)
        # await self.format_resp()
        return self

    def ret(self) -> list[QuoteProduct]:
        return self.products
