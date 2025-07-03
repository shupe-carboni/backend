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

from app.friedrich.requests.action_base import Login
from app.friedrich.requests.get_quotes import GetQuotes
