from dotenv import load_dotenv; load_dotenv()
import os
import logging
from random import randint
from asyncio import sleep
from fastapi import FastAPI, Request, status, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.routing import Match
## Routers ##
from app import relationships
from app.vendors import vendors
from app.customers import customers, customer_rel
from app.places import places, place_rel
from app.adp import (
    adp, adp_quotes, adp_quote_rel,
    coil_progs, ah_progs, prog_parts,
    prog_ratings
)

logger = logging.getLogger('uvicorn.info')

class BotTarpit(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        for route in app.routes:
            match_, scope = route.matches(request)
            if match_ == Match.FULL or path == '/favicon.ico':
                if (route.path == '/' and any(request.query_params._dict.keys())):
                    logging.info('Allowed passthrough of request on the root endpoint')
                return await call_next(request)
        host = request.client.host
        await self.trigger_delay(host, path)
        return Response(status_code=status.HTTP_301_MOVED_PERMANENTLY,content="Sorry, this resource has moved.")

    @staticmethod
    async def trigger_delay(host: str, path: str):
        delay = randint(10,100)
        logger.info(f'Honeypot triggered by {host} on {path}. Delaying for {delay}s')
        await sleep(delay)
    
app = FastAPI()
ORIGINS = os.getenv('ORIGINS')
ORIGINS_REGEX = os.getenv('ORIGINS_REGEX')

app.add_middleware(BotTarpit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_origin_regex=ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

## order matters
# customers
customers.include_router(customer_rel)
# places
places.include_router(place_rel)
# adp
adp_quotes.include_router(adp_quote_rel)
adp.include_router(adp_quotes)
adp.include_router(coil_progs)
adp.include_router(ah_progs)
adp.include_router(prog_parts)
adp.include_router(prog_ratings)
# combine
app.include_router(relationships)
app.include_router(vendors)
app.include_router(customers)
app.include_router(places)
app.include_router(adp)

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