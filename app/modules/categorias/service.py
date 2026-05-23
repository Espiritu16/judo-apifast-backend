from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.categorias.repository import CategoriaRepository
from app.shared.exceptions import DominioError
from app.shared.normalization import normalize_text


class CategoriaService:
    def __init__(self, db: Session):
        self.repo = CategoriaRepository(db)
        self.db = db

    def crear_categoria(self, payload: dict, user_id: int) -> dict:
        self._validar_payload(payload)
        self._validar_duplicado_nombre(payload['nombre_categoria'])
        try:
            item = self.repo.create(payload, user_id)
            self.db.commit()
            self.db.refresh(item)
            return self._to_dict(item)
        except IntegrityError as exc:
            self.db.rollback()
            raise DominioError('DUPLICATE_RESOURCE', 'Ya existe una categoría con ese nombre.', 409) from exc

    def listar_categorias(self) -> list[dict]:
        rows = self.repo.list_all()
        return [self._to_dict(r) for r in rows]

    def obtener_categoria(self, id_categoria: int) -> dict:
        r = self.repo.get(id_categoria)
        if not r:
            raise DominioError('RESOURCE_NOT_FOUND', 'Categoría no encontrada.', 404)
        return self._to_dict(r)

    def actualizar_categoria(self, id_categoria: int, payload: dict, user_id: int) -> dict:
        self._validar_payload(payload)
        r = self.repo.get(id_categoria)
        if not r:
            raise DominioError('RESOURCE_NOT_FOUND', 'Categoría no encontrada.', 404)

        if self._is_same_categoria(r, payload):
            raise DominioError('NO_CHANGES_DETECTED', 'No se detectaron cambios para guardar.', 400)

        self._validar_duplicado_nombre(payload['nombre_categoria'], id_actual=id_categoria)

        try:
            self.repo.update(r, payload, user_id)
            self.db.commit()
            self.db.refresh(r)
            return self._to_dict(r)
        except IntegrityError as exc:
            self.db.rollback()
            raise DominioError('DUPLICATE_RESOURCE', 'Ya existe una categoría con ese nombre.', 409) from exc

    def inactivar_categoria(self, id_categoria: int, motivo: str, user_id: int) -> dict:
        r = self.repo.get(id_categoria)
        if not r:
            raise DominioError('RESOURCE_NOT_FOUND', 'Categoría no encontrada.', 404)
        self.repo.inactivate(r, motivo, user_id)
        self.db.commit()
        self.db.refresh(r)
        return self._to_dict(r)

    def _validar_payload(self, payload: dict) -> None:
        nombre = (payload.get('nombre_categoria') or '').strip()
        if len(nombre) < 3 or len(nombre) > 80:
            raise DominioError('VALIDATION_ERROR', 'El nombre de categoría debe tener entre 3 y 80 caracteres.', 400)
        descripcion = (payload.get('descripcion') or '').strip()
        if len(descripcion) > 255:
            raise DominioError('VALIDATION_ERROR', 'La descripción no puede superar los 255 caracteres.', 400)
        payload['nombre_categoria'] = nombre
        payload['descripcion'] = descripcion or None

    def _validar_duplicado_nombre(self, nombre: str, id_actual: int | None = None) -> None:
        objetivo = normalize_text(nombre)
        for cat in self.repo.list_all():
            if id_actual and cat.id_categoria == id_actual:
                continue
            if normalize_text(cat.nombre_categoria) == objetivo:
                raise DominioError('DUPLICATE_RESOURCE', f'La categoría "{cat.nombre_categoria}" ya existe.', 409)

    def _is_same_categoria(self, actual, payload: dict) -> bool:
        return normalize_text(actual.nombre_categoria) == normalize_text(payload.get('nombre_categoria')) and normalize_text(actual.descripcion) == normalize_text(payload.get('descripcion'))

    def _to_dict(self, r) -> dict:
        return {
            'id_categoria': r.id_categoria,
            'nombre_categoria': r.nombre_categoria,
            'descripcion': r.descripcion,
            'estado': r.estado,
        }
