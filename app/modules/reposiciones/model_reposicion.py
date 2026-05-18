from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
"Modelo que representa la tabla Reposicion de la base de datos en MySQL en formato Python"
class Reposicion(Base):
    __tablename__ = 'reposicion'
    id_reposicion: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    codigo_reposicion: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    id_proveedor: Mapped[int] = mapped_column(BigInteger, ForeignKey('proveedor.id_proveedor'), nullable=False)
    fecha_solicitud: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    fecha_recepcion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    estado_reposicion: Mapped[str] = mapped_column(String(12), nullable=False, server_default='BORRADOR')
    observacion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fecha_creacion: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    creado_por: Mapped[int] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_edicion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    editado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    __table_args__ = (
        CheckConstraint("estado_reposicion IN ('BORRADOR', 'SOLICITADA', 'RECIBIDA', 'CERRADA', 'ANULADA')", name='ck_repo_estado_app'),
    )