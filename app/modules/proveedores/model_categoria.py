from sqlalchemy import BigInteger, Boolean, ForeignKey, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProveedorCategoria(Base):
    __tablename__ = 'proveedor_categoria'

    id_proveedor_categoria: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    id_proveedor: Mapped[int] = mapped_column(BigInteger, ForeignKey('proveedor.id_proveedor'), nullable=False)
    id_categoria: Mapped[int] = mapped_column(BigInteger, ForeignKey('categoria.id_categoria'), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default='1')

    fecha_creacion: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    creado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    fecha_edicion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    editado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    fecha_inactivacion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    inactivado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    motivo_inactivacion: Mapped[str | None] = mapped_column(String(255), nullable=True)
