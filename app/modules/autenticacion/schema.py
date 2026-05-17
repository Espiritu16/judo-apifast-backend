from pydantic import BaseModel
class LoginRequest(BaseModel):
    nombre_usuario: str
    clave: str
class TokenData(BaseModel):
    access_token: str
    token_type: str = 'bearer'
class UsuarioMe(BaseModel):
    id_usuario: int
    nombre_usuario: str
    nombre_completo: str
    rol: str