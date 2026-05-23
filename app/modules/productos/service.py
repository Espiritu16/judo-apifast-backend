from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.categorias.model import Categoria
from app.modules.productos.repository import ProductosRepository
from app.shared.exceptions import DominioError
from app.shared.normalization import normalize_text


class ProductoService:
    def __init__(self, db: Session):
        self.repo = ProductosRepository(db)
        self.db = db

    def crear_producto(self, payload: dict, user_id: int) -> dict:
        self._validar_payload(payload, is_create=True)
        self._validar_categoria(payload['id_categoria'])
        self._validar_duplicado_nombre(payload['nombre_producto'])
        try:
            item = self.repo.create(payload, user_id)
            self.db.commit()
            self.db.refresh(item)
            return self._to_dict(item)
        except IntegrityError as exc:
            self.db.rollback()
            raise DominioError('DUPLICATE_RESOURCE', 'Ya existe un producto con ese código o nombre.', 409) from exc

    def listar_productos(self) -> list[dict]:
        return [self._to_dict(r) for r in self.repo.list_all()]

    def obtener_producto(self, id_producto: int) -> dict:
        r = self.repo.get(id_producto)
        if not r:
            raise DominioError('RESOURCE_NOT_FOUND', 'Producto no encontrado.', 404)
        return self._to_dict(r)

    def actualizar_producto(self, id_producto: int, payload: dict, user_id: int) -> dict:
        self._validar_payload(payload, is_create=False)
        r = self.repo.get(id_producto)
        if not r:
            raise DominioError('RESOURCE_NOT_FOUND', 'Producto no encontrado.', 404)
        self._validar_categoria(payload['id_categoria'])

        if self._is_same_producto(r, payload):
            raise DominioError('NO_CHANGES_DETECTED', 'No se detectaron cambios para guardar.', 400)

        self._validar_duplicado_nombre(payload['nombre_producto'], id_actual=id_producto)

        try:
            self.repo.update(r, payload, user_id)
            self.db.commit()
            self.db.refresh(r)
            return self._to_dict(r)
        except IntegrityError as exc:
            self.db.rollback()
            raise DominioError('DUPLICATE_RESOURCE', 'Ya existe un producto con ese código o nombre.', 409) from exc

    def inactivar_producto(self, id_producto: int, motivo: str, user_id: int) -> dict:
        r = self.repo.get(id_producto)
        if not r:
            raise DominioError('RESOURCE_NOT_FOUND', 'Producto no encontrado.', 404)
        self.repo.inactivate(r, motivo, user_id)
        self.db.commit()
        self.db.refresh(r)
        return self._to_dict(r)

    def _validar_payload(self, payload: dict, is_create: bool) -> None:
        nombre = (payload.get('nombre_producto') or '').strip()
        if len(nombre) < 3 or len(nombre) > 120:
            raise DominioError('VALIDATION_ERROR', 'El nombre de producto debe tener entre 3 y 120 caracteres.', 400)
        unidad = (payload.get('unidad_medida') or '').strip()
        if not unidad or len(unidad) > 20:
            raise DominioError('VALIDATION_ERROR', 'La presentación/unidad de medida es obligatoria y no puede superar 20 caracteres.', 400)
        descripcion = (payload.get('descripcion') or '').strip()
        if len(descripcion) > 255:
            raise DominioError('VALIDATION_ERROR', 'La descripción no puede superar 255 caracteres.', 400)
        costo = payload.get('costo_unitario_actual')
        if costo is None or float(costo) < 0:
            raise DominioError('VALIDATION_ERROR', 'El costo unitario debe ser mayor o igual a 0.', 400)
        if is_create:
            codigo = (payload.get('codigo_producto') or '').strip()
            if not codigo:
                raise DominioError('VALIDATION_ERROR', 'El código de producto es obligatorio.', 400)
            payload['codigo_producto'] = codigo
        payload['nombre_producto'] = nombre
        payload['unidad_medida'] = unidad
        payload['descripcion'] = descripcion or None

    def _validar_categoria(self, id_categoria: int) -> None:
        categoria = self.db.get(Categoria, id_categoria)
        if not categoria or categoria.estado != 'ACTIVO':
            raise DominioError('RESOURCE_NOT_FOUND', 'Categoría no encontrada o inactiva.', 404)

    def _validar_duplicado_nombre(self, nombre: str, id_actual: int | None = None) -> None:
        objetivo = normalize_text(nombre)
        for prod in self.repo.list_all():
            if id_actual and prod.id_producto == id_actual:
                continue
            if normalize_text(prod.nombre_producto) == objetivo:
                raise DominioError('DUPLICATE_RESOURCE', f'El producto "{prod.nombre_producto}" ya existe.', 409)

    def _is_same_producto(self, actual, payload: dict) -> bool:
        return (
            normalize_text(actual.nombre_producto) == normalize_text(payload.get('nombre_producto'))
            and normalize_text(actual.descripcion) == normalize_text(payload.get('descripcion'))
            and int(actual.id_categoria) == int(payload.get('id_categoria'))
            and normalize_text(actual.unidad_medida) == normalize_text(payload.get('unidad_medida'))
            and float(actual.costo_unitario_actual) == float(payload.get('costo_unitario_actual'))
        )

    def _to_dict(self, r) -> dict:
        return {
            'id_producto': r.id_producto,
            'codigo_producto': r.codigo_producto,
            'nombre_producto': r.nombre_producto,
            'descripcion': r.descripcion,
            'id_categoria': r.id_categoria,
            'unidad_medida': r.unidad_medida,
            'costo_unitario_actual': float(r.costo_unitario_actual),
            'estado': r.estado,
            'creado_por': r.creado_por,
            'fecha_creacion': r.fecha_creacion,
            'editado_por': r.editado_por,
            'fecha_edicion': r.fecha_edicion,
            'inactivado_por': r.inactivado_por,
            'fecha_inactivacion': r.fecha_inactivacion,
        }
