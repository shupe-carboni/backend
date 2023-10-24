from fastapi import FastAPI, Header, HTTPException, Depends, Request
from typing import Annotated, Optional
from starlette.responses import RedirectResponse
from app.quotes.quotes import quotes
from app.jsonapi import JSONAPI_CONTENT_TYPE

app = FastAPI()

async def application_vnd_json(
        request: Request,
        content_type: Annotated[str, Header()]=None,
    ) -> None:
    if request.method in ('GET', 'DELETE'):
        return
    elif content_type != JSONAPI_CONTENT_TYPE:
        raise HTTPException(status_code=415)

vnd_json = Depends(application_vnd_json)
depends = [vnd_json]
app.include_router(quotes, dependencies=depends)

@app.get('/')
async def home():
    return RedirectResponse('/docs')