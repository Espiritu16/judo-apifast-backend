from sqlalchemy.orm import Session
from app.core.security import crear_token_acceso, verify_password
from app.modules.autenticacion.repository import AutenteicacionRepository
from app.modules.usuarios.model import Usuario
from app.shared.exceptions import DominioError
"Clase servicio que ayudará a crear las APIs en el  router de autenticación"
class AutenticacionService:
    def __init__(self,db:Session):
        self.repo=AutenteicacionRepository(db)
        self.db=db
    def login(self, nombre_usuario: str, clave: str) -> dict:
        user = self.repo.get_by_username(self.db, nombre_usuario)
        if not user or user.estado != 'ACTIVO' or not verify_password(clave, user.clave_hash):
            raise DominioError('CREDENCIALES_INVALIDAS', 'Usuario o clave incorrecta', 401)
        token = crear_token_acceso({'sub': str(user.id_usuario), 'rol': user.rol})
        return {'access_token': token, 'token_type': 'bearer'}
    def me(user: Usuario) -> dict:
        return {
            'id_usuario': user.id_usuario,
            'nombre_usuario': user.nombre_usuario,
            'nombre_completo': user.nombre_completo,
            'rol': user.rol,
        }