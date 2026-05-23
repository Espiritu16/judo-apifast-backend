import re
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.modules.usuarios.repository import UsuarioRepository
from app.shared.exceptions import DominioError
from app.shared.normalization import normalize_text


EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
VALID_ROLES = {'DUEÑA', 'EMPLEADO'}
VALID_ESTADOS = {'ACTIVO', 'INACTIVO'}


class UsuarioService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UsuarioRepository(db)

    def listar_usuarios(self) -> list[dict]:
        return [self._to_dict(u) for u in self.repo.list_all()]

    def obtener_usuario(self, id_usuario: int) -> dict:
        user = self.repo.get(id_usuario)
        if not user:
            raise DominioError('USER_NOT_FOUND', 'El usuario seleccionado ya no existe.', 404)
        return self._to_dict(user)

    def listar_roles(self) -> list[dict]:
        return [
            {'codigo': 'DUEÑA', 'etiqueta': 'Administradora'},
            {'codigo': 'EMPLEADO', 'etiqueta': 'Empleado'},
        ]

    def crear_usuario(self, payload: dict, actor_id: int) -> dict:
        self._validar_payload_create(payload)

        email = payload['correo']
        if self.repo.get_by_email(email):
            raise DominioError('EMAIL_ALREADY_EXISTS', 'Ya existe un usuario registrado con este correo.', 409)

        nombres = payload.pop('nombres')
        apellidos = payload.pop('apellidos', None)
        password = payload.pop('password')

        payload['nombre_completo'] = self._build_full_name(nombres, apellidos)
        payload['correo'] = email
        payload['rol'] = self._normalize_role(payload['rol'])
        payload['estado'] = self._normalize_estado(payload.get('estado', 'ACTIVO'))
        payload['clave_hash'] = hash_password(password)

        item = self.repo.create(payload, actor_id)
        self.db.commit()
        self.db.refresh(item)
        return self._to_dict(item)

    def actualizar_usuario(self, id_usuario: int, payload: dict, actor_id: int) -> dict:
        self._validar_payload_update(payload)

        user = self.repo.get(id_usuario)
        if not user:
            raise DominioError('USER_NOT_FOUND', 'El usuario seleccionado ya no existe.', 404)

        correo_nuevo = payload['correo'].strip().lower()
        if correo_nuevo != user.correo:
            by_mail = self.repo.get_by_email(correo_nuevo)
            if by_mail and by_mail.id_usuario != id_usuario:
                raise DominioError('EMAIL_ALREADY_EXISTS', 'Ya existe un usuario registrado con este correo.', 409)

        nombre_nuevo = self._build_full_name(payload['nombres'], payload.get('apellidos'))
        rol_nuevo = self._normalize_role(payload['rol'])
        estado_nuevo = self._normalize_estado(payload['estado'])

        no_changes = (
            normalize_text(user.nombre_completo) == normalize_text(nombre_nuevo)
            and user.correo == correo_nuevo
            and self._normalize_role(user.rol) == rol_nuevo
            and self._normalize_estado(user.estado) == estado_nuevo
        )
        if no_changes:
            raise DominioError('NO_CHANGES_DETECTED', 'No se detectaron cambios para guardar.', 400)

        updated = self.repo.update(
            user,
            {
                'nombre_completo': nombre_nuevo,
                'correo': correo_nuevo,
                'rol': rol_nuevo,
                'estado': estado_nuevo,
            },
            actor_id,
        )
        self.db.commit()
        self.db.refresh(updated)
        return self._to_dict(updated)

    def actualizar_estado(self, id_usuario: int, estado: str, motivo: str | None, actor_id: int) -> dict:
        user = self.repo.get(id_usuario)
        if not user:
            raise DominioError('USER_NOT_FOUND', 'El usuario seleccionado ya no existe.', 404)

        estado_norm = self._normalize_estado(estado)
        if self._normalize_estado(user.estado) == estado_norm:
            raise DominioError('NO_CHANGES_DETECTED', 'No se detectaron cambios para guardar.', 400)

        updated = self.repo.set_estado(user, estado_norm, actor_id, motivo)
        self.db.commit()
        self.db.refresh(updated)
        return self._to_dict(updated)

    def _validar_payload_create(self, payload: dict) -> None:
        self._validar_base(payload)
        pwd = (payload.get('password') or '').strip()
        if not pwd:
            raise DominioError('VALIDATION_ERROR', 'La contraseña es obligatoria al crear usuario.', 400)
        if len(pwd) < 8:
            raise DominioError('VALIDATION_ERROR', 'La contraseña debe tener al menos 8 caracteres.', 400)

    def _validar_payload_update(self, payload: dict) -> None:
        self._validar_base(payload)

    def _validar_base(self, payload: dict) -> None:
        nombres = (payload.get('nombres') or '').strip()
        apellidos = (payload.get('apellidos') or '').strip()
        correo = (payload.get('correo') or '').strip().lower()

        if not nombres:
            raise DominioError('VALIDATION_ERROR', 'El nombre es obligatorio.', 400)
        if not correo:
            raise DominioError('VALIDATION_ERROR', 'El correo es obligatorio.', 400)
        if not EMAIL_RE.match(correo):
            raise DominioError('VALIDATION_ERROR', 'El correo debe tener un formato válido.', 400)

        payload['nombres'] = nombres
        payload['apellidos'] = apellidos or None
        payload['correo'] = correo

        role = payload.get('rol')
        if not role:
            raise DominioError('VALIDATION_ERROR', 'El rol es obligatorio.', 400)
        self._normalize_role(role)

        estado = payload.get('estado', 'ACTIVO')
        self._normalize_estado(estado)

    def _normalize_role(self, role: str) -> str:
        clean = role.strip().upper()
        clean = clean.replace('ADMINISTRADOR', 'DUEÑA').replace('DUENA', 'DUEÑA')
        if clean not in VALID_ROLES:
            raise DominioError('INVALID_ROLE', 'No se permite crear usuarios con roles inválidos.', 400)
        return clean

    def _normalize_estado(self, estado: str) -> str:
        clean = (estado or '').strip().upper()
        if clean not in VALID_ESTADOS:
            raise DominioError('VALIDATION_ERROR', 'El estado debe ser ACTIVO o INACTIVO.', 400)
        return clean

    def _build_full_name(self, nombres: str, apellidos: str | None) -> str:
        joined = f"{nombres.strip()} {(apellidos or '').strip()}".strip()
        if not joined:
            raise DominioError('VALIDATION_ERROR', 'El nombre es obligatorio.', 400)
        return joined

    def _split_name(self, nombre_completo: str) -> tuple[str, str | None]:
        value = (nombre_completo or '').strip()
        if not value:
            return '', None
        parts = value.split()
        if len(parts) == 1:
            return parts[0], None
        return parts[0], ' '.join(parts[1:])

    def _to_dict(self, user) -> dict:
        nombres, apellidos = self._split_name(user.nombre_completo)
        return {
            'id_usuario': user.id_usuario,
            'nombres': nombres,
            'apellidos': apellidos,
            'nombre_completo': user.nombre_completo,
            'correo': user.correo,
            'rol': user.rol,
            'estado': user.estado,
            'fecha_creacion': user.fecha_creacion,
            'fecha_actualizacion': user.fecha_edicion,
        }
