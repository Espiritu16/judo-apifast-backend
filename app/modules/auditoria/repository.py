from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auditoria.model import AuditoriaEvento


class AuditoriaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> AuditoriaEvento:
        item = AuditoriaEvento(**data)
        self.db.add(item)
        self.db.flush()
        return item

    def list_all(
        self,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        modulo: str | None = None,
        accion: str | None = None,
        resultado: str | None = None,
        id_usuario: int | None = None,
        limit: int = 100,
    ) -> list[AuditoriaEvento]:
        stmt = select(AuditoriaEvento)
        if desde:
            stmt = stmt.where(AuditoriaEvento.fecha_creacion >= desde)
        if hasta:
            stmt = stmt.where(AuditoriaEvento.fecha_creacion <= hasta)
        if modulo:
            stmt = stmt.where(AuditoriaEvento.modulo == modulo)
        if accion:
            stmt = stmt.where(AuditoriaEvento.accion == accion)
        if resultado:
            stmt = stmt.where(AuditoriaEvento.resultado == resultado)
        if id_usuario:
            stmt = stmt.where(AuditoriaEvento.id_usuario == id_usuario)
        stmt = stmt.order_by(AuditoriaEvento.id_auditoria.desc()).limit(limit)
        return self.db.execute(stmt).scalars().all()
