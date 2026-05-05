from fastapi import FastAPI

from app.core.config import settings
from app.core.router import api_router

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get('/salud', tags=['salud'])
def salud() -> dict[str, str]:
    return {'estado': 'ok'}
