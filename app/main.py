from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import os
import uvicorn
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.router import api_router
from app.core.security import decodificar_token
from app.modules.auditoria.service import AuditoriaService
from app.shared.exceptions import DominioError

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://proyectoutp.com",
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
async def dominio_error_handler(request: Request, exc: DominioError):
    _registrar_auditoria_error(
        request,
        accion="ERROR_DOMINIO",
        resultado="ERROR",
        codigo_error=exc.codigo,
        mensaje=exc.mensaje,
        status_code=exc.status_code,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "codigo": exc.codigo, "mensaje": exc.mensaje},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    errores = [
        {
            "campo": ".".join(str(part) for part in e.get("loc", [])),
            "mensaje": e.get("msg", "Dato inválido"),
        }
        for e in exc.errors()
    ]
    _registrar_auditoria_error(
        request,
        accion="ERROR_VALIDACION",
        resultado="ERROR",
        codigo_error="VALIDATION_ERROR",
        mensaje="Datos inválidos en la solicitud.",
        status_code=400,
        metadata={"errores": errores},
    )
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
async def http_exception_handler(request: Request, exc: HTTPException):
    resultado = "DENEGADO" if exc.status_code in (401, 403) else "ERROR"
    if exc.status_code == 403:
        _registrar_auditoria_error(
            request,
            accion="PERMISO_DENEGADO",
            resultado=resultado,
            codigo_error="PERMISSION_DENIED",
            mensaje="No tienes permisos para esta acción con tu rol actual.",
            status_code=403,
        )
        return JSONResponse(
            status_code=403,
            content={
                "ok": False,
                "codigo": "PERMISSION_DENIED",
                "mensaje": "No tienes permisos para esta acción con tu rol actual.",
            },
        )
    if exc.status_code == 404:
        _registrar_auditoria_error(
            request,
            accion="HTTP_ERROR",
            resultado=resultado,
            codigo_error="RESOURCE_NOT_FOUND",
            mensaje=str(exc.detail),
            status_code=404,
        )
        return JSONResponse(
            status_code=404,
            content={"ok": False, "codigo": "RESOURCE_NOT_FOUND", "mensaje": str(exc.detail)},
        )
    if exc.status_code == 400:
        _registrar_auditoria_error(
            request,
            accion="HTTP_ERROR",
            resultado=resultado,
            codigo_error="VALIDATION_ERROR",
            mensaje=str(exc.detail),
            status_code=400,
        )
        return JSONResponse(
            status_code=400,
            content={"ok": False, "codigo": "VALIDATION_ERROR", "mensaje": str(exc.detail)},
        )
    _registrar_auditoria_error(
        request,
        accion="HTTP_ERROR",
        resultado=resultado,
        codigo_error="HTTP_ERROR",
        mensaje=str(exc.detail),
        status_code=exc.status_code,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "codigo": "HTTP_ERROR", "mensaje": str(exc.detail)},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, __: IntegrityError):
    _registrar_auditoria_error(
        request,
        accion="ERROR_INTEGRIDAD",
        resultado="ERROR",
        codigo_error="DUPLICATE_RESOURCE",
        mensaje="El recurso ya existe y entra en conflicto con un dato único.",
        status_code=409,
    )
    return JSONResponse(
        status_code=409,
        content={
            "ok": False,
            "codigo": "DUPLICATE_RESOURCE",
            "mensaje": "El recurso ya existe y entra en conflicto con un dato único.",
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, __: Exception):
    _registrar_auditoria_error(
        request,
        accion="ERROR_INTERNO",
        resultado="ERROR",
        codigo_error="INTERNAL_ERROR",
        mensaje="Error interno del servidor.",
        status_code=500,
    )
    return JSONResponse(
        status_code=500,
        content={"ok": False, "codigo": "INTERNAL_ERROR", "mensaje": "Error interno del servidor."},
    )


def _registrar_auditoria_error(
    request: Request,
    accion: str,
    resultado: str,
    codigo_error: str,
    mensaje: str,
    status_code: int,
    metadata: dict | None = None,
) -> None:
    db = SessionLocal()
    try:
        AuditoriaService(db).registrar_evento(
            accion=accion,
            modulo=_resolver_modulo(request),
            resultado=resultado,
            id_usuario=_resolver_usuario_id(request),
            codigo_error=codigo_error,
            mensaje=mensaje,
            metodo=request.method,
            ruta=request.url.path,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            metadata={"status_code": status_code, **(metadata or {})},
        )
    except Exception:
        db.rollback()
    finally:
        db.close()


def _resolver_modulo(request: Request) -> str:
    parts = [part for part in request.url.path.split("/") if part]
    if "api" in parts:
        api_index = parts.index("api")
        if len(parts) > api_index + 2:
            return parts[api_index + 2]
    return parts[0] if parts else "sistema"


def _resolver_usuario_id(request: Request) -> int | None:
    auth = request.headers.get("authorization", "")
    prefix = "bearer "
    if not auth.lower().startswith(prefix):
        return None
    try:
        payload = decodificar_token(auth[len(prefix):].strip())
        sub = payload.get("sub")
        return int(sub) if sub is not None else None
    except (TypeError, ValueError):
        return None


app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get('/salud', tags=['salud'])
def salud() -> dict[str, str]:
    return {'estado': 'ok'}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
