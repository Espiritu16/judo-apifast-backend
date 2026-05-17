from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
"Clase que modela la tabla categoría de la base de datos"
class Categoria(Base):
    __tablename__ = 'categoria'
    id_categoria: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nombre_categoria: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estado: Mapped[str] = mapped_column(String(10), nullable=False, server_default='ACTIVO')
    fecha_creacion: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    creado_por: Mapped[int] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_edicion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    editado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    fecha_inactivacion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    inactivado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    motivo_inactivacion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    __table_args__ = (
        CheckConstraint("estado IN ('ACTIVO', 'INACTIVO')", name='ck_categoria_estado_app'),
    )