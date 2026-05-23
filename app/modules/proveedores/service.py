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
            item = self.repo.create(payload, user_id)
            self.db.commit()
            self.db.refresh(item)
            return self._to_dict(item)
        except IntegrityError as exc:
            self.db.rollback()
            raise DominioError('DATO_DUPLICADO', 'Proveedor duplicado', 409) from exc
    def listar_proveedores(self) -> list[dict]:
        rows = self.repo.list_all()
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
        r = self.repo.get(id_proveedor)
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
        r = self.repo.get(id_proveedor)
        if not r:
            raise DominioError('PROVEEDOR_NO_ENCONTRADO', 'Proveedor no encontrado', 404)
        self.repo.update(r, payload, user_id)
        self.db.commit()
        self.db.refresh(r)
        return self._to_dict(r)
    def inactivar_proveedor(self, id_proveedor: int, motivo: str, user_id: int) -> dict:
        r = self.repo.get(id_proveedor)
        if not r:
            raise DominioError('PROVEEDOR_NO_ENCONTRADO', 'Proveedor no encontrado', 404)
        self.repo.inactivate(r, motivo, user_id)
        self.db.commit()
        self.db.refresh(r)
        return self._to_dict(r)

    def _to_dict(self, r) -> dict:
        return {
            'id_proveedor': r.id_proveedor,
            'razon_social': r.razon_social,
            'ruc': r.ruc,
            'telefono': r.telefono,
            'correo_electronico': r.correo_electronico,
            'estado': r.estado,
        }
