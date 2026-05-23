from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.proveedores.model import Proveedor
"Clase repositorio que contendrá funciones que se utilizan en Service de proveedores"
class ProveedorRepository:
    def __init__(self,db:Session):
        self.db = db
    def create(self, data: dict, user_id: int) -> Proveedor:
        item = Proveedor(**data, creado_por=user_id)
        self.db.add(item)
        self.db.flush()
        self.db.refresh(item)
        return item
    def list_all(self) -> list[Proveedor]:
        return self.db.execute(select(Proveedor).order_by(Proveedor.id_proveedor.desc())).scalars().all()
    def get(self, id_proveedor: int) -> Proveedor | None:
        return self.db.get(Proveedor, id_proveedor)
    def exists_by_document(self, document: str) -> bool:
        stmt = select(Proveedor.id_proveedor).where(Proveedor.numero_documento == document).limit(1)
        return self.db.execute(stmt).first() is not None
    def update(self, item: Proveedor, data: dict, user_id: int) -> Proveedor:
        for k, v in data.items():
            setattr(item, k, v)
        item.editado_por = user_id
        item.fecha_edicion = datetime.utcnow()
        return item
    def inactivate(self, item: Proveedor, motivo: str, user_id: int) -> Proveedor:
        item.estado = 'INACTIVO'
        item.inactivado_por = user_id
        item.motivo_inactivacion = motivo
        item.fecha_inactivacion = datetime.utcnow()
        return item
