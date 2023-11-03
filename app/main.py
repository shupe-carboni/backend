from fastapi import FastAPI
from starlette.responses import RedirectResponse
from app.quotes.quotes import quotes

app = FastAPI()

app.include_router(quotes)

@app.get('/')
async def home():
    return RedirectResponse('/docs')