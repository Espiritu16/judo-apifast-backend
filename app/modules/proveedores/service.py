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

        ruc = (payload.get('ruc') or '').strip()
        if ruc and (not ruc.isdigit() or len(ruc) not in (8, 11)):
            raise DominioError(
                'VALIDATION_ERROR',
                'El documento debe tener 8 dígitos para DNI o 11 dígitos para RUC.',
                400,
            )

        telefono = (payload.get('telefono') or '').strip()
        if len(telefono) > 20:
            raise DominioError('VALIDATION_ERROR', 'El teléfono no puede superar 20 caracteres.', 400)

        correo = (payload.get('correo_electronico') or '').strip().lower()
        if len(correo) > 120:
            raise DominioError('VALIDATION_ERROR', 'El correo no puede superar 120 caracteres.', 400)

        payload['razon_social'] = razon
        payload['ruc'] = ruc or None
        payload['telefono'] = telefono or None
        payload['correo_electronico'] = correo or None

    def _validar_duplicados(self, payload: dict, id_actual: int | None = None) -> None:
        target_razon = normalize_text(payload.get('razon_social'))
        target_ruc = (payload.get('ruc') or '').strip()
        for prov in self.repo.list_all():
            if id_actual and prov.id_proveedor == id_actual:
                continue
            if normalize_text(prov.razon_social) == target_razon:
                raise DominioError('DUPLICATE_RESOURCE', f'El proveedor "{prov.razon_social}" ya existe.', 409)
            if target_ruc and prov.ruc and prov.ruc.strip() == target_ruc:
                raise DominioError('DUPLICATE_RESOURCE', f'El RUC {target_ruc} ya está registrado.', 409)

    def _is_same_proveedor(self, actual, payload: dict) -> bool:
        return (
            normalize_text(actual.razon_social) == normalize_text(payload.get('razon_social'))
            and normalize_text(actual.ruc) == normalize_text(payload.get('ruc'))
            and normalize_text(actual.telefono) == normalize_text(payload.get('telefono'))
            and normalize_text(actual.correo_electronico) == normalize_text(payload.get('correo_electronico'))
        )

    def _to_dict(self, r) -> dict:
        return {
            'id_proveedor': r.id_proveedor,
            'razon_social': r.razon_social,
            'ruc': r.ruc,
            'telefono': r.telefono,
            'correo_electronico': r.correo_electronico,
            'estado': r.estado,
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
