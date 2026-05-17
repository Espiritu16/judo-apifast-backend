from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
class Usuario(Base):
    __tablename__ = 'usuario'
    id_usuario: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nombre_usuario: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(120), nullable=False)
    rol: Mapped[str] = mapped_column(String(30), nullable=False)
    estado: Mapped[str] = mapped_column(String(10), nullable=False, server_default='ACTIVO')
    clave_hash: Mapped[str] = mapped_column(String(255), nullable=False, server_default='')
    fecha_creacion: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    creado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    fecha_edicion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    editado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    fecha_inactivacion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    inactivado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    motivo_inactivacion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    __table_args__ = (
        CheckConstraint("estado IN ('ACTIVO', 'INACTIVO')", name='ck_usuario_estado_app'),
    )