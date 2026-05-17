from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)
def crear_token_acceso(data: dict, expire_minutes: int | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes or settings.JWT_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise ValueError('Token invalido') from exc