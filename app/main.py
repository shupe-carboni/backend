from fastapi import FastAPI, Header, HTTPException, Depends
from typing import Annotated
from starlette.responses import RedirectResponse
from app.quotes.quotes import quotes
from app.jsonapi import JSONAPI_CONTENT_TYPE

app = FastAPI()

async def application_vnd_json(content_type: Annotated[str, Header()]) -> None:
    if content_type != JSONAPI_CONTENT_TYPE:
        raise HTTPException(status_code=415)

vnd_json = Depends(application_vnd_json)
depends = [vnd_json]
app.include_router(quotes, dependencies=depends)

@app.get('/')
async def home():
    return RedirectResponse('/docs')