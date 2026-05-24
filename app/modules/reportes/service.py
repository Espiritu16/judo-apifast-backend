from datetime import date
from sqlalchemy.orm import Session
from app.modules.reportes.repository import ReportesRepository
from app.shared.exceptions import DominioError
"""Clase servicio que ayudará a crear las funciones que permiten el funcionamiento 
de las APIs en el  router de reportes"""
class ReporteService:
    def __init__(self,db:Session):
        self.db=db
        self.repo=ReportesRepository(db)
    def _validar_rango(self, desde: date | None, hasta: date | None) -> None:
        if desde and hasta and desde > hasta:
            raise DominioError('VALIDATION_ERROR', 'La fecha inicial no puede ser mayor que la fecha final.', 400)

    def reporte_valorizacion(self, desde: date | None = None, hasta: date | None = None) -> dict:
        self._validar_rango(desde, hasta)
        rows = self.repo.fetch_valorizacion(desde, hasta)
        total = sum(float(r.valor_producto) for r in rows)
        return {
            'total_valorizado': total,
            'items': [
                {
                    'id_producto': r.id_producto,
                    'nombre_producto': r.nombre_producto,
                    'categoria': r.nombre_categoria,
                    'stock_actual': float(r.stock_actual),
                    'costo_unitario_actual': float(r.costo_unitario_actual),
                    'valor_producto': float(r.valor_producto),
                }
                for r in rows
            ],
        }

    def reporte_rotacion(self, desde: date | None = None, hasta: date | None = None) -> list[dict]:
        self._validar_rango(desde, hasta)
        rows = self.repo.fetch_rotacion(desde, hasta)
        data = []
        for r in rows:
            base = float(r.stock_actual) if float(r.stock_actual) > 0 else 1.0
            data.append(
                {
                    'id_producto': r.id_producto,
                    'nombre_producto': r.nombre_producto,
                    'id_categoria': r.id_categoria,
                    'categoria': r.nombre_categoria,
                    'cantidad_salida': float(r.cantidad_salida),
                    'rotacion': float(r.cantidad_salida) / base,
                }
            )
        return data

    def reporte_stock_critico(self, desde: date | None = None, hasta: date | None = None) -> list[dict]:
        self._validar_rango(desde, hasta)
        rows = self.repo.fetch_stock_critico(desde, hasta)
        return [
            {
                'id_producto': p.id_producto,
                'nombre_producto': p.nombre_producto,
                'stock_actual': float(pi.stock_actual),
                'stock_minimo': float(pi.stock_minimo),
                'stock_maximo': float(pi.stock_maximo),
            }
            for p, pi in rows
            if float(pi.stock_actual) <= float(pi.stock_minimo)
        ]
