import aiohttp
from logging import getLogger

from app.friedrich.requests.action_base import Action

logger = getLogger("uvicorn.info")


class GetQuoteOpportunityInfo(Action):
    def __init__(self, req_session: aiohttp.ClientSession, quote_id) -> None:
        super().__init__(req_session)
        self.path: str = "Ajax_CreateQuoteLoadSelectedQuote.aspx"
        self.params = {"QuoteID": quote_id}
        self.quote_id = quote_id

        self.opp_id: str
        self.zip_code: int
        self.tax_exempt: bool
        self.price_level_id: str
        self.quote_shipments: int
        self.quote_notes: str

    def format_resp(self) -> "GetQuoteOpportunityInfo":
        resp_array = self.resp_raw.split("^")

        self.opp_id: str = resp_array[0]
        try:
            self.zip_code: int = int(resp_array[16])
        except:
            self.zip_code = None
        self.tax_exempt: bool = resp_array[17] == "Y"
        self.price_level_id: str = resp_array[7]
        self.quote_shipments: int = int(resp_array[10])
        self.quote_notes: str = resp_array[9]

        return self

    def ret(self) -> str:
        return self.opp_id
