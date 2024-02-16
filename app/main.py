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

@app.get('/test-db')
async def test_db():
    import psycopg2
    from dotenv import load_dotenv; load_dotenv()
    conn_params = {
        'database': os.environ.get('RDS_DB_NAME'),
        'host': os.environ.get('RDS_HOSTNAME'),
        'password': os.environ.get('RDS_PASSWORD'),
        'port': os.environ.get('RDS_PORT'),
        'user': os.environ.get('RDS_USER')
    }
    assert_failure = f"env vars not properly initiatlized\nname={conn_params['database']}\nhost={conn_params['host']}\npw={conn_params['password']}\nport={conn_params['host']}\nun={conn_params['user']}"
    if not all(list(conn_params.values())):
        return {'assertion_failure': assert_failure}
    conn = psycopg2.connect(**conn_params)
    try:
        with conn as cur:
            cur.execute('SELECT version();')
            db_version = cur.fetchone()
            return {'db_version': db_version}
    except Exception:
        import traceback as tb
        return {'error_tb': tb.format_exc()}

    finally:
        conn.close()