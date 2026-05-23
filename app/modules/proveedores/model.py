from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
"Modelo que representa la tabla Proveedor de la base de datos en MySQL en formato Python"
class Proveedor(Base):
    __tablename__ = 'proveedor'
    id_proveedor: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    razon_social: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo_documento: Mapped[str] = mapped_column(String(3), nullable=False)
    numero_documento: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    nombre_completo_persona: Mapped[str | None] = mapped_column(String(180), nullable=True)
    ruc: Mapped[str | None] = mapped_column(String(11), unique=True, nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    correo_electronico: Mapped[str | None] = mapped_column(String(120), nullable=True)
    direccion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    departamento: Mapped[str | None] = mapped_column(String(80), nullable=True)
    provincia: Mapped[str | None] = mapped_column(String(80), nullable=True)
    distrito: Mapped[str | None] = mapped_column(String(80), nullable=True)
    estado_contribuyente: Mapped[str | None] = mapped_column(String(50), nullable=True)
    condicion_contribuyente: Mapped[str | None] = mapped_column(String(50), nullable=True)
    estado: Mapped[str] = mapped_column(String(10), nullable=False, server_default='ACTIVO')

    fecha_creacion: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    creado_por: Mapped[int] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_edicion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    editado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)

    fecha_inactivacion: Mapped[str | None] = mapped_column(TIMESTAMP, nullable=True)
    inactivado_por: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('usuario.id_usuario'), nullable=True)
    motivo_inactivacion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        CheckConstraint("estado IN ('ACTIVO', 'INACTIVO')", name='ck_proveedor_estado_app'),
        CheckConstraint("tipo_documento IN ('DNI', 'RUC')", name='ck_proveedor_tipo_documento_app'),
    )
