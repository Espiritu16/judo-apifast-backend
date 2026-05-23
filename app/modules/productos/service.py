from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.categorias.model import Categoria
from app.modules.productos.repository import ProductosRepository
from app.shared.exceptions import DominioError
"""Clase servicio que ayudará a crear las funciones que permiten el funcionamiento 
de las APIs en el  router de productos"""
class ProductoService:
    def __init__(self, db: Session):
        """Inicializa el repositorio compartiendo la misma sesión de BD."""
        self.repo = ProductosRepository(db)
        self.db = db
    def crear_producto(self, payload: dict, user_id: int) -> dict:
        categoria = self.db.get(Categoria, payload['id_categoria'])
        if not categoria or categoria.estado != 'ACTIVO':
            raise DominioError('CATEGORIA_NO_ENCONTRADA', 'Categoria no encontrada o inactiva', 404)
        try:
            item = self.repo.create(payload, user_id)
            self.db.commit()
            self.db.refresh(item)
            return self._to_dict(item)
        except IntegrityError as exc:
            self.db.rollback()
            raise DominioError('DATO_DUPLICADO', 'Producto duplicado', 409) from exc
    def listar_productos(self) -> list[dict]:
        rows = self.repo.list_all()
        return [
            {
                'id_producto': r.id_producto,
                'codigo_producto': r.codigo_producto,
                'nombre_producto': r.nombre_producto,
                'descripcion': r.descripcion,
                'id_categoria': r.id_categoria,
                'unidad_medida': r.unidad_medida,
                'costo_unitario_actual': float(r.costo_unitario_actual),
                'estado': r.estado,
            }
            for r in rows
        ]
    def obtener_producto(self, id_producto: int) -> dict:
        r = self.repo.get(id_producto)
        if not r:
            raise DominioError('PRODUCTO_NO_ENCONTRADO', 'Producto no encontrado', 404)
        return {
            'id_producto': r.id_producto,
            'codigo_producto': r.codigo_producto,
            'nombre_producto': r.nombre_producto,
            'descripcion': r.descripcion,
            'id_categoria': r.id_categoria,
            'unidad_medida': r.unidad_medida,
            'costo_unitario_actual': float(r.costo_unitario_actual),
            'estado': r.estado,
        }
    def actualizar_producto(self, id_producto: int, payload: dict, user_id: int) -> dict:
        r = self.repo.get(id_producto)
        if not r:
            raise DominioError('PRODUCTO_NO_ENCONTRADO', 'Producto no encontrado', 404)
        categoria = self.db.get(Categoria, payload['id_categoria'])
        if not categoria or categoria.estado != 'ACTIVO':
            raise DominioError('CATEGORIA_NO_ENCONTRADA', 'Categoria no encontrada o inactiva', 404)
        self.repo.update(r, payload, user_id)
        self.db.commit()
        self.db.refresh(r)
        return self._to_dict(r)
    def inactivar_producto(self, id_producto: int, motivo: str, user_id: int) -> dict:
        r = self.repo.get(id_producto)
        if not r:
            raise DominioError('PRODUCTO_NO_ENCONTRADO', 'Producto no encontrado', 404)
        self.repo.inactivate(r, motivo, user_id)
        self.db.commit()
        self.db.refresh(r)
        return self._to_dict(r)

    def _to_dict(self, r) -> dict:
        return {
            'id_producto': r.id_producto,
            'codigo_producto': r.codigo_producto,
            'nombre_producto': r.nombre_producto,
            'descripcion': r.descripcion,
            'id_categoria': r.id_categoria,
            'unidad_medida': r.unidad_medida,
            'costo_unitario_actual': float(r.costo_unitario_actual),
            'estado': r.estado,
        }
