import aiohttp
from logging import getLogger

from app.friedrich.models import *
from app.friedrich.requests import action_base, get_quote_opportunity_info

GetQuoteOpportunityInfo = get_quote_opportunity_info.GetQuoteOpportunityInfo
Action = action_base.Action

logger = getLogger("uvicorn.info")


class GetQuoteProjectDetails(Action):
    def __init__(self, req_session: aiohttp.ClientSession, quote_id) -> None:
        super().__init__(req_session)
        self.path: str = "Ajax_CreateQuoteLoadSelectedProject.aspx"
        self.details = None
        self.quote_id = quote_id
        self.params = {}
        self.opp_info: GetQuoteOpportunityInfo

    async def make_request(self):
        opp_info: GetQuoteOpportunityInfo = await GetQuoteOpportunityInfo(
            self.req_session, self.quote_id
        ).make_request()
        # store for later use in getting products
        self.opp_info = opp_info.format_resp()
        self.params.update({"OpportunityID": self.opp_info.opp_id})
        return await super().make_request()

    def format_resp(self) -> "GetQuoteProjectDetails":
        """
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
