from fastapi import FastAPI
from starlette.responses import RedirectResponse
## Routers ##
from app import relationships
from app.quotes import quotes
from app.vendors import vendors

app = FastAPI()

app.include_router(relationships)
app.include_router(vendors)
app.include_router(quotes)

@app.get('/')
async def home():
    return RedirectResponse('/docs')