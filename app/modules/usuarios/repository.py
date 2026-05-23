from app.shared.dates import now_lima_naive
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.usuarios.model import Usuario


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Usuario]:
        return self.db.execute(select(Usuario).order_by(Usuario.id_usuario.desc())).scalars().all()

    def get(self, id_usuario: int) -> Usuario | None:
        return self.db.get(Usuario, id_usuario)

    def get_by_email(self, correo: str) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.correo == correo)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, data: dict, actor_id: int) -> Usuario:
        item = Usuario(**data, creado_por=actor_id)
        self.db.add(item)
        self.db.flush()
        self.db.refresh(item)
        return item

    def update(self, item: Usuario, data: dict, actor_id: int) -> Usuario:
        for k, v in data.items():
            setattr(item, k, v)
        item.editado_por = actor_id
        item.fecha_edicion = now_lima_naive()
        return item

    def set_estado(self, item: Usuario, estado: str, actor_id: int, motivo: str | None = None) -> Usuario:
        item.estado = estado
        if estado == 'INACTIVO':
            item.inactivado_por = actor_id
            item.fecha_inactivacion = now_lima_naive()
            item.motivo_inactivacion = motivo or 'Inactivación manual'
        else:
            item.inactivado_por = None
            item.fecha_inactivacion = None
            item.motivo_inactivacion = None
            item.editado_por = actor_id
            item.fecha_edicion = now_lima_naive()
        return item
