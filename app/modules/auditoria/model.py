from sqlalchemy import BigInteger, JSON, String, TIMESTAMP, func, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


BigIntPrimaryKey = BigInteger().with_variant(Integer, "sqlite")


class AuditoriaEvento(Base):
    __tablename__ = "auditoria_evento"

    id_auditoria: Mapped[int] = mapped_column(BigIntPrimaryKey, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    accion: Mapped[str] = mapped_column(String(80), nullable=False)
    modulo: Mapped[str] = mapped_column(String(50), nullable=False)
    entidad: Mapped[str | None] = mapped_column(String(80), nullable=True)
    id_entidad: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    resultado: Mapped[str] = mapped_column(String(20), nullable=False)
    codigo_error: Mapped[str | None] = mapped_column(String(80), nullable=True)
    mensaje: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metodo: Mapped[str | None] = mapped_column(String(10), nullable=True)
    ruta: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    fecha_creacion: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
