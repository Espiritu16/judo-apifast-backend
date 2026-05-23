from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_db
from app.modules.autenticacion.schema import LoginRequest
from app.modules.autenticacion.service import AutenticacionService as AutenticacionServ
from app.modules.usuarios.model import Usuario
from app.shared.responses import respuesta_ok
router = APIRouter()
"Espacio donde se encuentran las APIs relacionadas a la autenticación"
"""API que sirve para enviar el nombre de usuario y contraseña 
que digita una persona en el login al servidor"""
@router.post('/login')
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return respuesta_ok('Login exitoso', AutenticacionServ(db).login(payload.nombre_usuario, payload.clave))
"API para saber si un usuario ha sido autenticado"
@router.get('/me')
def me(user: Usuario = Depends(get_current_user)):
    return respuesta_ok('Usuario autenticado', AutenticacionServ.me(user))
