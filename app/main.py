from dotenv import load_dotenv; load_dotenv()
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
## Routers ##
from app import relationships
from app.quotes import quotes, quote_rel
from app.vendors import vendors
from app.customers import customers, customer_rel
from app.locations import location_rel
from app.places import places, place_rel
from app.products import product_rel
from app.adp import adp

app = FastAPI()
ORIGINS = os.getenv('ORIGINS')
ORIGINS_REGEX = os.getenv('ORIGINS_REGEX')

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
places.include_router(place_rel)
app.include_router(places)
app.include_router(product_rel)
app.include_router(adp)
app.include_router(relationships)

@app.get('/')
async def home():
    return RedirectResponse('/docs')

@app.get('/test-db')
async def test_db():
    from app.db import Database
    try:
        db = Database()
        test = db.test()
        return {'db_version': test}
    except Exception:
        import traceback as tb
        return {
            'error_tb': tb.format_exc(),
        }