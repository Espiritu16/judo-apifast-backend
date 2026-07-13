from datetime import date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.modules.inventario.model_movimiento import MovimientoInventario
from app.modules.inventario.model_parametro import ParametroInventario
from app.modules.movimientos.repository import MovimientoRepository
from app.modules.productos.model import Producto
from app.modules.usuarios.model import Usuario
from app.shared.exceptions import DominioError

LIMA_TZ = ZoneInfo("America/Lima")

# Tipos generales nuevos
TIPOS_GENERALES = {"ENTRADA", "SALIDA", "AJUSTE"}
# Tipos legacy todavía aceptados para compatibilidad
TIPOS_LEGACY = {"MERMA", "AJUSTE_POSITIVO", "AJUSTE_NEGATIVO"}
TIPOS_VALIDOS_FILTRO = TIPOS_GENERALES | TIPOS_LEGACY

MOTIVOS_POR_TIPO = {
    "ENTRADA": {
        "COMPRA_PROVEEDOR",
        "DEVOLUCION_CLIENTE",
        "REGISTRO_INICIAL",
        "CORRECCION_ENTRADA",
    },
    "SALIDA": {
        "VENTA",
        "MERMA",
        "DEVOLUCION_PROVEEDOR",
        "CONSUMO_INTERNO",
        "PERDIDA_DANIO",
    },
    "AJUSTE": {
        "CONTEO_FISICO",
        "CORRECCION_MANUAL",
        "REGULARIZACION",
        "INCREMENTO_AJUSTE",
        "DISMINUCION_AJUSTE",
    },
}

MOTIVOS_AJUSTE_INCREMENTO = {"INCREMENTO_AJUSTE"}
MOTIVOS_AJUSTE_DECREMENTO = {
    "CONTEO_FISICO",
    "CORRECCION_MANUAL",
    "REGULARIZACION",
    "DISMINUCION_AJUSTE",
}

MOTIVO_ALIAS_TO_CODIGO = {
    "recepcion de proveedor": "COMPRA_PROVEEDOR",
    "recepción de proveedor": "COMPRA_PROVEEDOR",
    "compra a proveedor": "COMPRA_PROVEEDOR",
    "devolucion de cliente": "DEVOLUCION_CLIENTE",
    "devolución de cliente": "DEVOLUCION_CLIENTE",
    "registro inicial de stock": "REGISTRO_INICIAL",
    "correccion de entrada": "CORRECCION_ENTRADA",
    "corrección de entrada": "CORRECCION_ENTRADA",
    "venta": "VENTA",
    "merma": "MERMA",
    "devolucion a proveedor": "DEVOLUCION_PROVEEDOR",
    "devolución a proveedor": "DEVOLUCION_PROVEEDOR",
    "consumo interno": "CONSUMO_INTERNO",
    "perdida o dano de producto": "PERDIDA_DANIO",
    "pérdida o daño de producto": "PERDIDA_DANIO",
    "revision de conteo": "CONTEO_FISICO",
    "revisión de conteo": "CONTEO_FISICO",
    "ajuste por conteo fisico": "CONTEO_FISICO",
    "ajuste por conteo físico": "CONTEO_FISICO",
    "correccion manual de stock": "CORRECCION_MANUAL",
    "corrección manual de stock": "CORRECCION_MANUAL",
    "regularizacion de inventario": "REGULARIZACION",
    "regularización de inventario": "REGULARIZACION",
    "incremento por ajuste": "INCREMENTO_AJUSTE",
    "disminucion por ajuste": "DISMINUCION_AJUSTE",
    "disminución por ajuste": "DISMINUCION_AJUSTE",
}


class MovimientoService:
    def __init__(self, db: Session):
        self.repo = MovimientoRepository(db)
        self.db = db

    def registrar_movimiento(self, payload: dict, user: Usuario) -> MovimientoInventario:
        return self._registrar_movimiento(payload, user, origen_interno=False)

    def registrar_movimiento_interno(self, payload: dict, user: Usuario) -> MovimientoInventario:
        return self._registrar_movimiento(payload, user, origen_interno=True)

    def _registrar_movimiento(self, payload: dict, user: Usuario, origen_interno: bool) -> MovimientoInventario:
        tipo_general, motivo_codigo = self._normalizar_tipo_y_motivo(
            payload.get("tipo_movimiento"),
            payload.get("motivo"),
        )

        if tipo_general == "ENTRADA" and not origen_interno:
            raise DominioError(
                "ENTRADA_MANUAL_NO_PERMITIDA",
                "Las entradas de inventario deben registrarse desde el módulo de Reposiciones.",
                400,
            )

        if tipo_general == "ENTRADA" and payload.get("costo_unitario") is None:
            raise DominioError("COSTO_REQUERIDO", "costo_unitario es obligatorio para ENTRADA", 400)

        producto = self.db.get(Producto, payload["id_producto"])
        if not producto or producto.estado != "ACTIVO":
            raise DominioError("PRODUCTO_NO_ENCONTRADO", "Producto no encontrado o inactivo", 404)

        parametro = self.db.get(ParametroInventario, payload["id_producto"])
        if not parametro:
            parametro = ParametroInventario(
                id_producto=payload["id_producto"],
                stock_actual=0,
                stock_minimo=0,
                stock_maximo=0,
                consumo_promedio_diario=0,
                stock_seguridad=0,
                tiempo_reposicion_dias=0,
                creado_por=user.id_usuario,
            )
            self.db.add(parametro)
            self.db.flush()

        cantidad = Decimal(str(payload["cantidad"]))
        stock_actual = Decimal(str(parametro.stock_actual))
        stock_seguridad = Decimal(str(parametro.stock_seguridad or 0))

        if tipo_general == "ENTRADA":
            costo_unitario = Decimal(str(payload.get("costo_unitario") or 0))
            precio_venta_producto = Decimal(str(producto.costo_unitario_actual or 0))
            if precio_venta_producto > 0 and costo_unitario > precio_venta_producto:
                raise DominioError(
                    "COSTO_SUPERA_PRECIO_VENTA",
                    "El costo unitario de entrada no puede ser mayor al precio de venta del producto.",
                    400,
                )

        if self._es_movimiento_salida(tipo_general, motivo_codigo):
            if stock_actual - cantidad < 0:
                raise DominioError("STOCK_INSUFICIENTE", "No hay stock suficiente para realizar la operacion", 409)
            if stock_actual - cantidad < stock_seguridad:
                raise DominioError(
                    "STOCK_SEGURIDAD_VIOLADA",
                    "La operación invade el stock de seguridad configurado para este producto.",
                    409,
                )

        if self._es_movimiento_entrada(tipo_general, motivo_codigo):
            self._validar_stock_maximo(parametro, cantidad)

        movimiento = MovimientoInventario(
            id_producto=payload["id_producto"],
            tipo_movimiento=tipo_general,
            cantidad=payload["cantidad"],
            costo_unitario=payload.get("costo_unitario"),
            motivo=motivo_codigo,
            referencia=payload.get("referencia"),
            observacion=payload.get("observacion"),
            creado_por=user.id_usuario,
        )
        self.db.add(movimiento)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(movimiento)
        return movimiento

    def listar_movimientos(
        self,
        desde: date | None = None,
        hasta: date | None = None,
        tipo: str | None = None,
        producto_id: int | None = None,
        categoria_id: int | None = None,
        motivo: str | None = None,
    ) -> list[dict]:
        self._validar_filtros(desde, hasta, tipo, producto_id, categoria_id, motivo)
        desde_dt, hasta_dt = self._rango_lima(desde, hasta)
        tipo_filtro = tipo.strip().upper() if tipo else None
        motivo_filtro = motivo.strip().upper() if motivo else None

        data = self.repo.list_all(
            desde=desde_dt,
            hasta=hasta_dt,
            tipo=tipo_filtro,
            producto_id=producto_id,
            categoria_id=categoria_id,
            motivo=motivo_filtro,
        )
        return [
            {
                "id_movimiento": m.id_movimiento,
                "id_producto": m.id_producto,
                "fecha_movimiento": m.fecha_movimiento,
                "tipo_movimiento": m.tipo_movimiento,
                "cantidad": float(m.cantidad),
                "costo_unitario": float(m.costo_unitario) if m.costo_unitario is not None else None,
                "motivo": m.motivo,
                "referencia": m.referencia,
                "observacion": m.observacion,
                "creado_por": m.creado_por,
                "fecha_creacion": m.fecha_creacion,
                "editado_por": m.editado_por,
                "fecha_edicion": m.fecha_edicion,
            }
            for m in data
        ]

    def obtener_movimiento(self, id_movimiento: int) -> dict | None:
        m = self.repo.get(id_movimiento)
        if not m:
            raise DominioError("RESOURCE_NOT_FOUND", "Movimiento no encontrado.", 404)
        return {
            "id_movimiento": m.id_movimiento,
            "id_producto": m.id_producto,
            "fecha_movimiento": m.fecha_movimiento,
            "tipo_movimiento": m.tipo_movimiento,
            "cantidad": float(m.cantidad),
            "costo_unitario": float(m.costo_unitario) if m.costo_unitario is not None else None,
            "motivo": m.motivo,
            "referencia": m.referencia,
            "observacion": m.observacion,
            "creado_por": m.creado_por,
            "fecha_creacion": m.fecha_creacion,
            "editado_por": m.editado_por,
            "fecha_edicion": m.fecha_edicion,
        }

    def _normalizar_tipo_y_motivo(self, tipo_in: str | None, motivo_in: str | None) -> tuple[str, str]:
        if not tipo_in:
            raise DominioError("VALIDATION_ERROR", "tipo_movimiento es obligatorio.", 400)
        raw_tipo = tipo_in.strip().upper()

        # Compatibilidad con tipos legacy
        if raw_tipo == "MERMA":
            tipo_general = "SALIDA"
            motivo_default = "MERMA"
        elif raw_tipo == "AJUSTE_POSITIVO":
            tipo_general = "AJUSTE"
            motivo_default = "INCREMENTO_AJUSTE"
        elif raw_tipo == "AJUSTE_NEGATIVO":
            tipo_general = "AJUSTE"
            motivo_default = "DISMINUCION_AJUSTE"
        elif raw_tipo in TIPOS_GENERALES:
            tipo_general = raw_tipo
            motivo_default = None
        else:
            raise DominioError("MOVIMIENTO_INVALIDO", "Tipo de movimiento no valido", 400)

        motivo_val = (motivo_in or "").strip()
        if not motivo_val:
            if motivo_default:
                return tipo_general, motivo_default
            raise DominioError("VALIDATION_ERROR", "Debe seleccionar un motivo del movimiento.", 400)

        motivo_upper = motivo_val.upper()
        if motivo_upper in MOTIVOS_POR_TIPO.get(tipo_general, set()):
            return tipo_general, motivo_upper

        alias = MOTIVO_ALIAS_TO_CODIGO.get(motivo_val.strip().lower())
        if alias and alias in MOTIVOS_POR_TIPO.get(tipo_general, set()):
            return tipo_general, alias

        raise DominioError(
            "VALIDATION_ERROR",
            f"El motivo '{motivo_val}' no es válido para el tipo {tipo_general}.",
            400,
        )

    def _es_movimiento_entrada(self, tipo_general: str, motivo_codigo: str) -> bool:
        if tipo_general == "ENTRADA":
            return True
        if tipo_general == "AJUSTE" and motivo_codigo in MOTIVOS_AJUSTE_INCREMENTO:
            return True
        return False

    def _es_movimiento_salida(self, tipo_general: str, motivo_codigo: str) -> bool:
        if tipo_general == "SALIDA":
            return True
        if tipo_general == "AJUSTE" and motivo_codigo in MOTIVOS_AJUSTE_DECREMENTO:
            return True
        return False

    def _validar_stock_maximo(self, parametro: ParametroInventario, cantidad: Decimal) -> None:
        stock_maximo = Decimal(str(parametro.stock_maximo or 0))
        if stock_maximo <= 0:
            return

        stock_actual = Decimal(str(parametro.stock_actual or 0))
        if stock_actual + cantidad > stock_maximo:
            raise DominioError(
                "STOCK_MAXIMO_SUPERADO",
                "Esta operación superaría el stock máximo configurado para el producto.",
                409,
            )

    def _rango_lima(self, desde: date | None, hasta: date | None) -> tuple[datetime | None, datetime | None]:
        desde_dt = None
        hasta_dt = None
        if desde:
            desde_dt = datetime.combine(desde, time.min).replace(tzinfo=LIMA_TZ).replace(tzinfo=None)
        if hasta:
            hasta_dt = datetime.combine(hasta, time.max).replace(tzinfo=LIMA_TZ).replace(tzinfo=None)
        return desde_dt, hasta_dt

    def _validar_filtros(
        self,
        desde: date | None,
        hasta: date | None,
        tipo: str | None,
        producto_id: int | None,
        categoria_id: int | None,
        motivo: str | None,
    ) -> None:
        if desde and hasta and desde > hasta:
            raise DominioError("VALIDATION_ERROR", "La fecha inicial no puede ser mayor que la fecha final.", 400)
        if tipo and tipo.strip().upper() not in TIPOS_VALIDOS_FILTRO:
            raise DominioError("VALIDATION_ERROR", f"Tipo de movimiento inválido: {tipo}", 400)
        if producto_id is not None and producto_id <= 0:
            raise DominioError("VALIDATION_ERROR", "productoId debe ser mayor que 0.", 400)
        if categoria_id is not None and categoria_id <= 0:
            raise DominioError("VALIDATION_ERROR", "categoriaId debe ser mayor que 0.", 400)
        if motivo and not motivo.strip():
            raise DominioError("VALIDATION_ERROR", "motivo no puede ser vacío.", 400)
