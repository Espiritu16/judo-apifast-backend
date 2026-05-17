from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decodificar_token
from app.modules.usuarios.model import Usuario
security = HTTPBearer(auto_error=False)
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Usuario:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='No autenticado')

    try:
        payload = decodificar_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token invalido')
    user_id = payload.get('sub')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token invalido')

    user = db.get(Usuario, int(user_id))
    if not user or user.estado != 'ACTIVO':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Usuario no valido')
    return user
def require_roles(*allowed: str):
    def _check(user: Usuario = Depends(get_current_user)) -> Usuario:
        if user.rol not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Sin permisos para esta operacion')
        return user

    return _check
