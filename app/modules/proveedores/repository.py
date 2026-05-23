from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.categorias.model import Categoria
from app.modules.proveedores.model_categoria import ProveedorCategoria
from app.modules.proveedores.model import Proveedor
"Clase repositorio que contendrá funciones que se utilizan en Service de proveedores"
class ProveedorRepository:
    def __init__(self,db:Session):
        self.db = db
    def create(self, data: dict, user_id: int) -> Proveedor:
        persist_data = {k: v for k, v in data.items() if k != 'categoria_ids'}
        item = Proveedor(**persist_data, creado_por=user_id)
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
            if k == 'categoria_ids':
                continue
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

    def list_active_category_ids(self, id_proveedor: int) -> list[int]:
        stmt = (
            select(ProveedorCategoria.id_categoria)
            .where(ProveedorCategoria.id_proveedor == id_proveedor, ProveedorCategoria.activo.is_(True))
            .order_by(ProveedorCategoria.id_categoria.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_category_names(self, categoria_ids: list[int]) -> list[str]:
        if not categoria_ids:
            return []
        stmt = (
            select(Categoria.nombre_categoria)
            .where(Categoria.id_categoria.in_(categoria_ids))
            .order_by(Categoria.nombre_categoria.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def categorias_existentes(self, categoria_ids: list[int]) -> set[int]:
        if not categoria_ids:
            return set()
        stmt = select(Categoria.id_categoria).where(Categoria.id_categoria.in_(categoria_ids))
        return set(self.db.execute(stmt).scalars().all())

    def replace_category_assignments(self, id_proveedor: int, categoria_ids: list[int], user_id: int) -> None:
        target = set(categoria_ids)
        stmt = select(ProveedorCategoria).where(ProveedorCategoria.id_proveedor == id_proveedor)
        rows = self.db.execute(stmt).scalars().all()
        by_categoria = {row.id_categoria: row for row in rows}
        now = datetime.utcnow()

        for categoria_id in target:
            current = by_categoria.get(categoria_id)
            if current:
                if not current.activo:
                    current.activo = True
                    current.fecha_edicion = now
                    current.editado_por = user_id
                    current.fecha_inactivacion = None
                    current.inactivado_por = None
                    current.motivo_inactivacion = None
                continue
            self.db.add(
                ProveedorCategoria(
                    id_proveedor=id_proveedor,
                    id_categoria=categoria_id,
                    activo=True,
                    creado_por=user_id,
                )
            )

        for categoria_id, current in by_categoria.items():
            if categoria_id in target:
                continue
            if current.activo:
                current.activo = False
                current.fecha_edicion = now
                current.editado_por = user_id
                current.fecha_inactivacion = now
                current.inactivado_por = user_id
                current.motivo_inactivacion = 'Desasignación de categoría'
