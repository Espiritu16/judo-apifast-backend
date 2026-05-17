from sqlalchemy import BigInteger, CheckConstraint, Computed, ForeignKey, Integer, Numeric, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
"Clase que representa la entidad Parametro_Inventario de la BD en MySQL"
class ParametroInventario(Base):
    __tablename__ = 'parametro_inventario'
    id_producto: Mapped[int] = mapped_column(BigInteger, ForeignKey('producto.id_producto'), primary_key=True)
    stock_actual: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, server_default='0')
    stock_minimo: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, server_default='0')
    stock_maximo: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, server_default='0')
    consumo_promedio_diario: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, server_default='0')
    stock_seguridad: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, server_default='0')
    tiempo_reposicion_dias: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')
    punto_reorden: Mapped[float] = mapped_column(
        Numeric(12, 2),
        Computed('(consumo_promedio_diario * tiempo_reposicion_dias) + stock_seguridad', persisted=True),
        nullable=False,
    )
    fecha_creacion: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    creado_por: Mapped[int] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_edicion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    editado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    __table_args__ = (
        CheckConstraint('stock_actual >= 0', name='ck_param_stock_actual_app'),
        CheckConstraint('stock_minimo >= 0', name='ck_param_stock_min_app'),
        CheckConstraint('stock_maximo >= stock_minimo', name='ck_param_stock_max_min_app'),
    )