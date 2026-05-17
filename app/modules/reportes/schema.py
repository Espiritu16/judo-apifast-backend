from pydantic import BaseModel
"""Clases que representan los datos que se transmitirán 
entre servidor y cliente a través de las APIs relacionadas al módulo de reportes"""
class ValorizacionItem(BaseModel):
    id_producto: int
    nombre_producto: str
    categoria: str
    stock_actual: float
    costo_unitario_actual: float
    valor_producto: float
class RotacionItem(BaseModel):
    id_producto: int
    nombre_producto: str
    cantidad_salida: float
    rotacion: float
