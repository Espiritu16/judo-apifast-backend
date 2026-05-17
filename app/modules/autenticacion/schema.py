from pydantic import BaseModel
"""Clases que representan los datos que se transmitirán 
entre servidor y cliente a través de las APIs relacionadas al módulo de autenticación"""
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