from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.proveedores.repository import ProveedorRepository
from app.shared.exceptions import DominioError
"""Clase servicio que ayudará a crear las funciones que permiten el funcionamiento 
de las APIs en el  router de proveedores"""
class ProveedorService:
    def __init__(self,db:Session):
        self.repo=ProveedorRepository(db)
        self.db=db
    def crear_proveedor(self, payload: dict, user_id: int) -> dict:
        try:
            item = self.repo.create(self.db, payload, user_id)
            self.db.commit()
            return {'id_proveedor': item.id_proveedor}
        except IntegrityError as exc:
            self.db.rollback()
            raise DominioError('DATO_DUPLICADO', 'Proveedor duplicado', 409) from exc
    def listar_proveedores(self) -> list[dict]:
        rows = self.repo.list_all(self.db)
        return [
            {
                'id_proveedor': r.id_proveedor,
                'razon_social': r.razon_social,
                'ruc': r.ruc,
                'telefono': r.telefono,
                'correo_electronico': r.correo_electronico,
                'estado': r.estado,
            }
            for r in rows
        ]
    def obtener_proveedor(self, id_proveedor: int) -> dict:
        r = self.repo.get(self.db, id_proveedor)
        if not r:
            raise DominioError('PROVEEDOR_NO_ENCONTRADO', 'Proveedor no encontrado', 404)
        return {
            'id_proveedor': r.id_proveedor,
            'razon_social': r.razon_social,
            'ruc': r.ruc,
            'telefono': r.telefono,
            'correo_electronico': r.correo_electronico,
            'estado': r.estado,
        }
    def actualizar_proveedor(self, id_proveedor: int, payload: dict, user_id: int) -> dict:
        r = self.repo.get(self.db, id_proveedor)
        if not r:
            raise DominioError('PROVEEDOR_NO_ENCONTRADO', 'Proveedor no encontrado', 404)
        self.repo.update(self.db, r, payload, user_id)
        self.db.commit()
        return {'id_proveedor': id_proveedor}
    def inactivar_proveedor(self, id_proveedor: int, motivo: str, user_id: int) -> dict:
        r = self.repo.get(self.db, id_proveedor)
        if not r:
            raise DominioError('PROVEEDOR_NO_ENCONTRADO', 'Proveedor no encontrado', 404)
        self.repo.inactivate(self.db, r, motivo, user_id)
        self.db.commit()
        return {'id_proveedor': id_proveedor}