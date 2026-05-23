from pydantic import BaseModel, Field
"""Clases que representan los datos que se transmitirán 
entre servidor y cliente a través de las APIs relacionadas al módulo de inventario"""
class ParametroInventarioUpdate(BaseModel):
    stock_minimo: float = Field(ge=0)
    stock_maximo: float = Field(ge=0)
    stock_seguridad: float = Field(ge=0)
    consumo_promedio_diario: float | None = Field(default=None, ge=0)
    tiempo_reposicion_dias: int | None = Field(default=None, ge=0)
class StockItem(BaseModel):
    id_producto: int
    nombre_producto: str
    stock_actual: float
    stock_minimo: float
    stock_maximo: float
    estado_stock: str
class StockCriticoItem(StockItem):
    cantidad_sugerida: float
