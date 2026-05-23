# Usuarios preestablecidos
from sqlalchemy import select
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.usuarios.model import Usuario
SEED_USERS = [
    {
        'id_usuario': 1001,
        'correo': 'duena@judo.local',
        'nombre_completo': 'Duena JUDO',
        'rol': 'DUENA',
        'estado': 'ACTIVO',
        'clave': 'Cambio123!',
    },
    {
        'id_usuario': 1002,
        'correo': 'empleado@judo.local',
        'nombre_completo': 'Empleado JUDO',
        'rol': 'EMPLEADO',
        'estado': 'ACTIVO',
        'clave': 'Cambio123!',
    },
]
def main() -> None:
    db = SessionLocal()
    try:
        for u in SEED_USERS:
            existing = db.execute(select(Usuario).where(Usuario.correo == u['correo'])).scalar_one_or_none()
            if existing:
                existing.nombre_completo = u['nombre_completo']
                existing.rol = u['rol']
                existing.estado = u['estado']
                existing.clave_hash = hash_password(u['clave'])
                continue
            db.add(
                Usuario(
                    id_usuario=u['id_usuario'],
                    correo=u['correo'],
                    nombre_completo=u['nombre_completo'],
                    rol=u['rol'],
                    estado=u['estado'],
                    clave_hash=hash_password(u['clave']),
                    creado_por=None,
                )
            )
        db.commit()
        print('seed users ok')
    finally:
        db.close()
if __name__ == '__main__':
    main()
