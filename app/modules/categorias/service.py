from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.categorias.repository import CategoriaRepository
from app.shared.exceptions import DominioError
"Clase servicio que ayudará a crear las APIs en el  router de categoría"
class CategoriaService:
    def __init__(self,db:Session):
        self.repo=CategoriaRepository(db)
        self.db=db
    def crear_categoria(self, payload: dict, user_id: int) -> dict:
        try:
            item = self.repo.create(self.db, payload, user_id)
            self.db.commit()
            return {'id_categoria': item.id_categoria}
        except IntegrityError as exc:
            self.db.rollback()
            raise DominioError('DATO_DUPLICADO', 'Categoria duplicada', 409) from exc
    def listar_categorias(self) -> list[dict]:
        rows = self.repository.list_all(self.db)
        return [
            {'id_categoria': r.id_categoria, 'nombre_categoria': r.nombre_categoria, 'descripcion': r.descripcion, 'estado': r.estado}
            for r in rows
        ]
    def obtener_categoria(self, id_categoria: int) -> dict:
        r = self.repo.get(self.db, id_categoria)
        if not r:
            raise DominioError('CATEGORIA_NO_ENCONTRADA', 'Categoria no encontrada', 404)
        return {'id_categoria': r.id_categoria, 'nombre_categoria': r.nombre_categoria, 'descripcion': r.descripcion, 'estado': r.estado}
    def actualizar_categoria(self, id_categoria: int, payload: dict, user_id: int) -> dict:
        r = self.repo.get(self.db, id_categoria)
        if not r:
            raise DominioError('CATEGORIA_NO_ENCONTRADA', 'Categoria no encontrada', 404)
        self.repo.update(self.db, r, payload, user_id)
        self.db.commit()
        return {'id_categoria': id_categoria}
    def inactivar_categoria(self, id_categoria: int, motivo: str, user_id: int) -> dict:
        r = self.repo.get(self.db, id_categoria)
        if not r:
            raise DominioError('CATEGORIA_NO_ENCONTRADA', 'Categoria no encontrada', 404)
        self.repo.inactivate(self.db, r, motivo, user_id)
        self.db.commit()
        return {'id_categoria': id_categoria}
