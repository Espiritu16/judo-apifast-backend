from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import os
import uvicorn
from app.core.config import settings
from app.core.router import api_router
from app.shared.exceptions import DominioError

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://judo.proyectoutp.com",
        "http://localhost:4200",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DominioError)
async def dominio_error_handler(_: Request, exc: DominioError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "codigo": exc.codigo, "mensaje": exc.mensaje},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(_: Request, exc: RequestValidationError):
    errores = [
        {
            "campo": ".".join(str(part) for part in e.get("loc", [])),
            "mensaje": e.get("msg", "Dato inválido"),
        }
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=400,
        content={
            "ok": False,
            "codigo": "VALIDATION_ERROR",
            "mensaje": "Datos inválidos en la solicitud.",
            "errores": errores,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    if exc.status_code == 403:
        return JSONResponse(
            status_code=403,
            content={
                "ok": False,
                "codigo": "PERMISSION_DENIED",
                "mensaje": "No tienes permisos para esta acción con tu rol actual.",
            },
        )
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"ok": False, "codigo": "RESOURCE_NOT_FOUND", "mensaje": str(exc.detail)},
        )
    if exc.status_code == 400:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "codigo": "VALIDATION_ERROR", "mensaje": str(exc.detail)},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "codigo": "HTTP_ERROR", "mensaje": str(exc.detail)},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(_: Request, __: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={
            "ok": False,
            "codigo": "DUPLICATE_RESOURCE",
            "mensaje": "El recurso ya existe y entra en conflicto con un dato único.",
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, __: Exception):
    return JSONResponse(
        status_code=500,
        content={"ok": False, "codigo": "INTERNAL_ERROR", "mensaje": "Error interno del servidor."},
    )


app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get('/salud', tags=['salud'])
def salud() -> dict[str, str]:
    return {'estado': 'ok'}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
