from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.modules.auditoria.model import AuditoriaEvento
from app.modules.auditoria.service import AuditoriaService


def test_registrar_evento_persiste_contexto_y_metadata():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine, tables=[AuditoriaEvento.__table__])

    db = TestingSessionLocal()
    try:
        evento = AuditoriaService(db).registrar_evento(
            accion="CREAR_PRODUCTO",
            modulo="productos",
            resultado="EXITO",
            id_usuario=7,
            entidad="producto",
            id_entidad=15,
            ip="127.0.0.1",
            user_agent="pytest",
            metadata={"codigo_producto": "SKU-001"},
        )

        guardado = db.get(AuditoriaEvento, evento.id_auditoria)

        assert guardado is not None
        assert guardado.accion == "CREAR_PRODUCTO"
        assert guardado.modulo == "productos"
        assert guardado.resultado == "EXITO"
        assert guardado.id_usuario == 7
        assert guardado.entidad == "producto"
        assert guardado.id_entidad == 15
        assert guardado.ip == "127.0.0.1"
        assert guardado.user_agent == "pytest"
        assert guardado.extra_metadata == {"codigo_producto": "SKU-001"}
    finally:
        db.close()
