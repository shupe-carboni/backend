__version__ = "1.2.4"
from dotenv import load_dotenv

load_dotenv()
import os
import logging
from random import randint
from asyncio import sleep
from fastapi import FastAPI, Request, status, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.routing import Match

## Routers ##
from app.hardcast import hardcast
from app.vendors import vendors, vendors_info
from app.customers import customers, customer_rel, customer_locations
from app.places import places
from app.adp import (
    adp,
    adp_quotes,
    adp_quote_products,
    coil_progs,
    ah_progs,
    prog_parts,
    prog_ratings,
    ratings_admin,
    adp_customers,
    adp_mat_grp_discs,
    adp_snps,
)

logger = logging.getLogger("uvicorn.info")


class BotTarpit(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        for route in app.routes:
            match_, scope = route.matches(request)
            if match_ == Match.FULL or path == "/favicon.ico":
                if route.path == "/" and any(request.query_params._dict.keys()):
                    logging.info(
                        'Allowed passthrough of request"\
                                 " on the root endpoint'
                    )
                return await call_next(request)
        host = request.client.host
        await self.trigger_delay(host, path)
        return Response(
            status_code=status.HTTP_301_MOVED_PERMANENTLY,
            content="Sorry, this resource has moved.",
        )

    @staticmethod
    async def trigger_delay(host: str, path: str):
        delay = randint(10, 20)
        logger.info(f"{host} - {path} - Honeypot triggered. Delaying for {delay}s")
        await sleep(delay)


with open("README.md", "r") as read_me:
    description = read_me.read()

app = FastAPI(
    title="Shupe Carboni Backend API", version=__version__, description=description
)
ORIGINS = os.getenv("ORIGINS")
ORIGINS_REGEX = os.getenv("ORIGINS_REGEX")

app.add_middleware(BotTarpit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_origin_regex=ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## NOTE: order really, really matters
## NOTE: prefixing instead of registering sub-resources with
##          their parent resources helps with
##          ordering paths correctly
for route, prefix, target in (
    (customer_rel, "", customers),
    (adp_quotes, "", adp),
    (adp_quote_products, "", adp),
    (adp_customers, "", adp),
    (coil_progs, "", adp),
    (ah_progs, "", adp),
    (prog_parts, "", adp),
    (prog_ratings, "", adp),
    (ratings_admin, "", adp),
    (adp_mat_grp_discs, "", adp),
    (adp_snps, "", adp),
    (vendors, "", app),
    (vendors_info, "", app),
    (customer_locations, "/customers", app),
    (customers, "", app),
    (places, "", app),
    (adp, "/vendors", app),
    (hardcast, "", app),
):
    resource_path = f"{prefix}{route.prefix}"
    try:
        target.include_router(route, prefix=prefix)
    except Exception:
        logger.critical(
            f"resource {resource_path} encountered an error when attempting to register"
        )
    else:
        logger.info(f"registered {resource_path} to {id(target)}")


@app.get("/")
async def home():
    return RedirectResponse("/redoc")


@app.get("/test-db")
async def test_db():
    from app.db import ADP_DB

    try:
        session = next(ADP_DB.get_db())
        test = ADP_DB.test(session=session)
        return {"db_version": test}
    except Exception:
        import traceback as tb

        return {
            "error_tb": tb.format_exc(),
        }


@app.get("/v2")
async def v2_available() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
