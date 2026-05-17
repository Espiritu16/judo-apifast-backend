from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.usuarios.model import Usuario
"Clase repositorio que contendrá métodos que se utilizan en Service"
class UsuarioRepository:
    def __init__(self, db: Session):
        """Inyecta la sesión de la base de datos al inicializar la clase."""
        self.db = db
        """Sirve para buscar un usuario por su nombre de usuario."""
    def get_by_username(self, nombre_usuario: str) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.nombre_usuario == nombre_usuario)
        return self.db.execute(stmt).scalar_one_or_none()
