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
app.include_router(relationships)

@app.get('/')
async def home():
    return RedirectResponse('/docs')