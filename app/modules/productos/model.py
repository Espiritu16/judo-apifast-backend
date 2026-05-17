from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Numeric, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
"Clase que muestra la tabla Producto de la base de datos en MySQL en formato Python"
class Producto(Base):
    __tablename__ = 'producto'
    id_producto: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    codigo_producto: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    nombre_producto: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    id_categoria: Mapped[int] = mapped_column(BigInteger, ForeignKey('categoria.id_categoria'), nullable=False)
    unidad_medida: Mapped[str] = mapped_column(String(20), nullable=False)
    costo_unitario_actual: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    estado: Mapped[str] = mapped_column(String(10), nullable=False, server_default='ACTIVO')
    fecha_creacion: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    creado_por: Mapped[int] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_edicion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    editado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    fecha_inactivacion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    inactivado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    motivo_inactivacion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    __table_args__ = (
        CheckConstraint("estado IN ('ACTIVO', 'INACTIVO')", name='ck_producto_estado_app'),
        CheckConstraint('costo_unitario_actual >= 0', name='ck_producto_costo_pos_app'),
    )
