from sqlalchemy.orm import Session

from app.modules.reportes.repository import ReportesRepository
"""Clase servicio que ayudará a crear las funciones que permiten el funcionamiento 
de las APIs en el  router de reportes"""
class ReporteService:
    def __init__(self,db:Session):
        self.db=db
        self.repo=ReportesRepository(db)
    def reporte_valorizacion(self) -> dict:
        rows = self.repo.fetch_valorizacion(self.db)
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
    def reporte_rotacion(self) -> list[dict]:
        rows =self.repo.fetch_rotacion(self.db)
        data = []
        for r in rows:
            base = float(r.stock_actual) if float(r.stock_actual) > 0 else 1.0
            data.append(
                {
                    'id_producto': r.id_producto,
                    'nombre_producto': r.nombre_producto,
                    'cantidad_salida': float(r.cantidad_salida),
                    'rotacion': float(r.cantidad_salida) / base,
                }
            )
        return data
    def reporte_stock_critico(self) -> list[dict]:
        rows = self.repo.fetch_stock_critico(self.db)
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
