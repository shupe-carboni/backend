from dotenv import load_dotenv; load_dotenv()
import os
import logging
from random import randint
from asyncio import sleep
from fastapi import FastAPI, Request, status, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
## Routers ##
from app import relationships
from app.quotes import quotes, quote_rel, product_rel
from app.vendors import vendors
from app.customers import customers, customer_rel
from app.locations import location_rel
# from app.places import places, place_rel
from app.adp import adp

logger = logging.getLogger('uvicorn.info')

class BotTarpit(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, trigger_strings: list=None):
        super().__init__(app)
        self.substrings = trigger_strings
    
    async def dispatch(self, request: Request, call_next):
        triggers = [substring for substring in self.substrings if substring in request.url.path]
        if triggers:
            delay = randint(10,100)
            logger.info(f'Honeypot triggered by {request.client.host} using {triggers} in the url. Delaying for {delay}s')
            logger.info(f'Delaying response for {delay}s')
            await sleep(delay)
            return Response(status_code=status.HTTP_301_MOVED_PERMANENTLY)
        return await call_next(request)

app = FastAPI()
ORIGINS = os.getenv('ORIGINS')
ORIGINS_REGEX = os.getenv('ORIGINS_REGEX')

app.add_middleware(BotTarpit, trigger_strings=['/.env', 'wp-admin', '/.zsh', '/.flask', '/env.', '/.git', '/.jnv', '/druid', '/.well-known'])
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_origin_regex=ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

## order matters
app.include_router(vendors)
quotes.include_router(quote_rel)
app.include_router(quotes)
customers.include_router(customer_rel)
app.include_router(customers)
app.include_router(location_rel)
# places.include_router(place_rel)
# app.include_router(places)
app.include_router(product_rel)
app.include_router(adp)
app.include_router(relationships)

@app.get('/')
async def home():
    return RedirectResponse('/docs')

@app.get('/test-db')
async def test_db():
    from app.db import ADP_DB
    try:
        session = next(ADP_DB.get_db())
        test = ADP_DB.test(session=session)
        return {'db_version': test}
    except Exception:
        import traceback as tb
        return {
            'error_tb': tb.format_exc(),
        }