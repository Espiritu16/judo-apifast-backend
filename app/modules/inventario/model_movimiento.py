from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Numeric, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
"Clase creada para representar la tabla Movimiento_Inventario de la BD en MYSQL"
class MovimientoInventario(Base):
    __tablename__ = 'movimiento_inventario'
    id_movimiento: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_producto: Mapped[int] = mapped_column(BigInteger, ForeignKey('producto.id_producto'), nullable=False)
    fecha_movimiento: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    tipo_movimiento: Mapped[str] = mapped_column(String(20), nullable=False)
    cantidad: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    costo_unitario: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    motivo: Mapped[str] = mapped_column(String(120), nullable=False)
    referencia: Mapped[str | None] = mapped_column(String(50), nullable=True)
    observacion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fecha_creacion: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    creado_por: Mapped[int] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_edicion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    editado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    __table_args__ = (
        CheckConstraint("tipo_movimiento IN ('ENTRADA','SALIDA','MERMA','AJUSTE_POSITIVO','AJUSTE_NEGATIVO')", name='ck_mov_tipo_app'),
        CheckConstraint('cantidad > 0', name='ck_mov_cantidad_pos_app'),
    )