from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.proveedores.factiliza_client import FactilizaClient
from app.modules.proveedores.repository import ProveedorRepository
from app.modules.proveedores.schema import (
    ConsultaDocumentoResponseDto,
    FactilizaDniResponseDto,
    FactilizaRucResponseDto,
)
from app.shared.exceptions import DominioError
from app.shared.normalization import normalize_text


class ProveedorService:
    def __init__(self, db: Session):
        self.repo = ProveedorRepository(db)
        self.db = db

    def crear_proveedor(self, payload: dict, user_id: int) -> dict:
        self._validar_payload(payload)
        self._validar_duplicados(payload)
        try:
            item = self.repo.create(payload, user_id)
            self.repo.replace_category_assignments(item.id_proveedor, payload.get('categoria_ids', []), user_id)
            self.db.commit()
            self.db.refresh(item)
            return self._to_dict(item)
        except IntegrityError as exc:
            self.db.rollback()
            raise DominioError('DUPLICATE_RESOURCE', 'Ya existe un proveedor con los mismos datos únicos.', 409) from exc

    def listar_proveedores(self) -> list[dict]:
        return [self._to_dict(r) for r in self.repo.list_all()]

    def obtener_proveedor(self, id_proveedor: int) -> dict:
        r = self.repo.get(id_proveedor)
        if not r:
            raise DominioError('RESOURCE_NOT_FOUND', 'Proveedor no encontrado.', 404)
        return self._to_dict(r)

    def actualizar_proveedor(self, id_proveedor: int, payload: dict, user_id: int) -> dict:
        self._validar_payload(payload)
        r = self.repo.get(id_proveedor)
        if not r:
            raise DominioError('RESOURCE_NOT_FOUND', 'Proveedor no encontrado.', 404)

        if self._is_same_proveedor(r, payload):
            raise DominioError('NO_CHANGES_DETECTED', 'No se detectaron cambios para guardar.', 400)

        self._validar_duplicados(payload, id_actual=id_proveedor)

        try:
            self.repo.update(r, payload, user_id)
            self.repo.replace_category_assignments(r.id_proveedor, payload.get('categoria_ids', []), user_id)
            self.db.commit()
            self.db.refresh(r)
            return self._to_dict(r)
        except IntegrityError as exc:
            self.db.rollback()
            raise DominioError('DUPLICATE_RESOURCE', 'Ya existe un proveedor con los mismos datos únicos.', 409) from exc

    def inactivar_proveedor(self, id_proveedor: int, motivo: str, user_id: int) -> dict:
        r = self.repo.get(id_proveedor)
        if not r:
            raise DominioError('RESOURCE_NOT_FOUND', 'Proveedor no encontrado.', 404)
        self.repo.inactivate(r, motivo, user_id)
        self.db.commit()
        self.db.refresh(r)
        return self._to_dict(r)

    def actualizar_categorias(self, id_proveedor: int, categoria_ids: list[int], user_id: int) -> dict:
        r = self.repo.get(id_proveedor)
        if not r:
            raise DominioError('RESOURCE_NOT_FOUND', 'Proveedor no encontrado.', 404)
        categoria_ids = self._normalizar_categoria_ids(categoria_ids)
        existentes = self.repo.categorias_existentes(categoria_ids)
        faltantes = sorted(set(categoria_ids) - existentes)
        if faltantes:
            raise DominioError('VALIDATION_ERROR', f'Categorías no válidas: {faltantes}', 400)
        self.repo.replace_category_assignments(id_proveedor, categoria_ids, user_id)
        self.db.commit()
        self.db.refresh(r)
        return self._to_dict(r)

    def listar_categorias(self, id_proveedor: int) -> dict:
        r = self.repo.get(id_proveedor)
        if not r:
            raise DominioError('RESOURCE_NOT_FOUND', 'Proveedor no encontrado.', 404)
        categoria_ids = self.repo.list_active_category_ids(id_proveedor)
        categorias = self.repo.list_category_names(categoria_ids)
        return {
            'id_proveedor': id_proveedor,
            'categoria_ids': categoria_ids,
            'categorias': categorias,
        }

    def consultar_documento_para_proveedor(self, documento: str) -> dict:
        documento_normalizado, tipo_documento = self._normalizar_y_validar_documento(documento)

        if self.repo.exists_by_document(documento_normalizado):
            raise DominioError('DUPLICATE_RESOURCE', 'Ya existe un proveedor registrado con este documento.', 409)

        factiliza_client = FactilizaClient()
        if tipo_documento == 'DNI':
            factiliza_raw = factiliza_client.consultar_dni(documento_normalizado)
            factiliza_data = FactilizaDniResponseDto.model_validate(factiliza_raw).data
            if not factiliza_data or not factiliza_data.numero:
                raise DominioError('RESOURCE_NOT_FOUND', 'No se encontraron datos para el documento ingresado.', 404)

            result = ConsultaDocumentoResponseDto(
                tipo_documento='DNI',
                numero_documento=factiliza_data.numero,
                nombre_o_razon_social=factiliza_data.nombre_completo or '',
                nombres=factiliza_data.nombres,
                apellido_paterno=factiliza_data.apellido_paterno,
                apellido_materno=factiliza_data.apellido_materno,
                direccion=factiliza_data.direccion,
                direccion_completa=factiliza_data.direccion_completa,
                departamento=factiliza_data.departamento,
                provincia=factiliza_data.provincia,
                distrito=factiliza_data.distrito,
            )
            return result.model_dump()

        factiliza_raw = factiliza_client.consultar_ruc(documento_normalizado)
        factiliza_data = FactilizaRucResponseDto.model_validate(factiliza_raw).data
        if not factiliza_data or not factiliza_data.numero:
            raise DominioError('RESOURCE_NOT_FOUND', 'No se encontraron datos para el documento ingresado.', 404)

        result = ConsultaDocumentoResponseDto(
            tipo_documento='RUC',
            numero_documento=factiliza_data.numero,
            nombre_o_razon_social=factiliza_data.nombre_o_razon_social or '',
            direccion=factiliza_data.direccion,
            direccion_completa=factiliza_data.direccion_completa,
            departamento=factiliza_data.departamento,
            provincia=factiliza_data.provincia,
            distrito=factiliza_data.distrito,
            estado_contribuyente=factiliza_data.estado,
            condicion_contribuyente=factiliza_data.condicion,
        )
        return result.model_dump()

    def _validar_payload(self, payload: dict) -> None:
        razon = (payload.get('razon_social') or '').strip()
        if len(razon) < 3 or len(razon) > 120:
            raise DominioError('VALIDATION_ERROR', 'La razón social debe tener entre 3 y 120 caracteres.', 400)

        tipo_documento = (payload.get('tipo_documento') or '').strip().upper()
        numero_documento = ''.join(ch for ch in (payload.get('numero_documento') or '').strip() if ch.isdigit())
        if tipo_documento not in ('DNI', 'RUC'):
            raise DominioError('VALIDATION_ERROR', 'El tipo de documento debe ser DNI o RUC.', 400)
        if tipo_documento == 'DNI' and len(numero_documento) != 8:
            raise DominioError('VALIDATION_ERROR', 'El documento debe tener 8 dígitos para DNI o 11 dígitos para RUC.', 400)
        if tipo_documento == 'RUC' and len(numero_documento) != 11:
            raise DominioError('VALIDATION_ERROR', 'El documento debe tener 8 dígitos para DNI o 11 dígitos para RUC.', 400)

        nombre_completo_persona = (payload.get('nombre_completo_persona') or '').strip()
        if tipo_documento == 'DNI' and not nombre_completo_persona:
            nombre_completo_persona = razon

        telefono = (payload.get('telefono') or '').strip()
        if len(telefono) > 20:
            raise DominioError('VALIDATION_ERROR', 'El teléfono no puede superar 20 caracteres.', 400)

        correo = (payload.get('correo_electronico') or '').strip().lower()
        if len(correo) > 120:
            raise DominioError('VALIDATION_ERROR', 'El correo no puede superar 120 caracteres.', 400)

        direccion = (payload.get('direccion') or '').strip()
        departamento = (payload.get('departamento') or '').strip()
        provincia = (payload.get('provincia') or '').strip()
        distrito = (payload.get('distrito') or '').strip()
        estado_contribuyente = (payload.get('estado_contribuyente') or '').strip()
        condicion_contribuyente = (payload.get('condicion_contribuyente') or '').strip()

        payload['razon_social'] = razon
        payload['tipo_documento'] = tipo_documento
        payload['numero_documento'] = numero_documento
        payload['nombre_completo_persona'] = nombre_completo_persona or None
        payload['telefono'] = telefono or None
        payload['correo_electronico'] = correo or None
        payload['direccion'] = direccion or None
        payload['departamento'] = departamento or None
        payload['provincia'] = provincia or None
        payload['distrito'] = distrito or None
        payload['estado_contribuyente'] = estado_contribuyente or None
        payload['condicion_contribuyente'] = condicion_contribuyente or None
        payload['categoria_ids'] = self._normalizar_categoria_ids(payload.get('categoria_ids', []))

        # Compatibilidad temporal con el campo antiguo ruc
        payload['ruc'] = numero_documento

        existentes = self.repo.categorias_existentes(payload['categoria_ids'])
        faltantes = sorted(set(payload['categoria_ids']) - existentes)
        if faltantes:
            raise DominioError('VALIDATION_ERROR', f'Categorías no válidas: {faltantes}', 400)

    def _validar_duplicados(self, payload: dict, id_actual: int | None = None) -> None:
        target_razon = normalize_text(payload.get('razon_social'))
        target_doc = (payload.get('numero_documento') or '').strip()
        for prov in self.repo.list_all():
            if id_actual and prov.id_proveedor == id_actual:
                continue
            if normalize_text(prov.razon_social) == target_razon:
                raise DominioError('DUPLICATE_RESOURCE', f'El proveedor "{prov.razon_social}" ya existe.', 409)
            if target_doc and prov.numero_documento and prov.numero_documento.strip() == target_doc:
                raise DominioError('DUPLICATE_RESOURCE', f'El documento {target_doc} ya está registrado.', 409)

    def _is_same_proveedor(self, actual, payload: dict) -> bool:
        return (
            normalize_text(actual.razon_social) == normalize_text(payload.get('razon_social'))
            and normalize_text(actual.tipo_documento) == normalize_text(payload.get('tipo_documento'))
            and normalize_text(actual.numero_documento) == normalize_text(payload.get('numero_documento'))
            and normalize_text(actual.nombre_completo_persona) == normalize_text(payload.get('nombre_completo_persona'))
            and normalize_text(actual.telefono) == normalize_text(payload.get('telefono'))
            and normalize_text(actual.correo_electronico) == normalize_text(payload.get('correo_electronico'))
            and normalize_text(actual.direccion) == normalize_text(payload.get('direccion'))
            and normalize_text(actual.departamento) == normalize_text(payload.get('departamento'))
            and normalize_text(actual.provincia) == normalize_text(payload.get('provincia'))
            and normalize_text(actual.distrito) == normalize_text(payload.get('distrito'))
            and normalize_text(actual.estado_contribuyente) == normalize_text(payload.get('estado_contribuyente'))
            and normalize_text(actual.condicion_contribuyente) == normalize_text(payload.get('condicion_contribuyente'))
        )

    def _to_dict(self, r) -> dict:
        categoria_ids = self.repo.list_active_category_ids(r.id_proveedor)
        categorias = self.repo.list_category_names(categoria_ids)
        return {
            'id_proveedor': r.id_proveedor,
            'razon_social': r.razon_social,
            'tipo_documento': r.tipo_documento,
            'numero_documento': r.numero_documento,
            'nombre_completo_persona': r.nombre_completo_persona,
            'telefono': r.telefono,
            'correo_electronico': r.correo_electronico,
            'direccion': r.direccion,
            'departamento': r.departamento,
            'provincia': r.provincia,
            'distrito': r.distrito,
            'estado_contribuyente': r.estado_contribuyente,
            'condicion_contribuyente': r.condicion_contribuyente,
            'estado': r.estado,
            'categoria_ids': categoria_ids,
            'categorias': categorias,
            # compatibilidad para pantallas antiguas
            'ruc': r.numero_documento,
        }

    def _normalizar_y_validar_documento(self, documento: str) -> tuple[str, str]:
        limpio = ''.join(ch for ch in (documento or '').strip() if ch.isdigit())
        if not limpio or len(limpio) not in (8, 11):
            raise DominioError(
                'VALIDATION_ERROR',
                'El documento debe tener 8 dígitos para DNI o 11 dígitos para RUC.',
                400,
            )
        tipo = 'DNI' if len(limpio) == 8 else 'RUC'
        return limpio, tipo

    def _normalizar_categoria_ids(self, categoria_ids: list[int] | None) -> list[int]:
        if not categoria_ids:
            return []
        cleaned = []
        for raw in categoria_ids:
            try:
                value = int(raw)
            except (TypeError, ValueError):
                raise DominioError('VALIDATION_ERROR', 'categoria_ids contiene valores no válidos.', 400)
            if value <= 0:
                raise DominioError('VALIDATION_ERROR', 'categoria_ids contiene valores no válidos.', 400)
            cleaned.append(value)
        return sorted(set(cleaned))
