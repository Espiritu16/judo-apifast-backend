from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from app.core.config import settings
from app.core.router import api_router

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# CORS: permite localhost en cualquier puerto y dominio productivo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://proyectoutp.com",
        "http://proyectoutp.com",
        "https://www.proyectoutp.com",
        "http://www.proyectoutp.com",
    ],
    allow_origin_regex=r"^https?://localhost(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)
@app.get('/salud', tags=['salud'])
def salud() -> dict[str, str]:
    return {'estado': 'ok'}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
