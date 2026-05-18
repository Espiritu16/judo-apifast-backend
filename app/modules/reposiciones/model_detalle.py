from sqlalchemy import BigInteger, ForeignKey, Numeric, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
"Modelo que representa la tabla Detalle_Reposicion de la base de datos en MySQL en formato Python"
class DetalleReposicion(Base):
    __tablename__ = 'detalle_reposicion'
    id_detalle_reposicion: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_reposicion: Mapped[int] = mapped_column(BigInteger, ForeignKey('reposicion.id_reposicion'), nullable=False)
    id_producto: Mapped[int] = mapped_column(BigInteger, ForeignKey('producto.id_producto'), nullable=False)
    cantidad_solicitada: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    cantidad_recibida: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, server_default='0')
    costo_unitario: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    fecha_creacion: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    creado_por: Mapped[int] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_edicion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    editado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
