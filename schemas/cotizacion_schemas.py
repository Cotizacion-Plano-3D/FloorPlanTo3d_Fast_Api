"""
Schemas para Cotización
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class MaterialCotizacion(BaseModel):
    """Material en la cotización"""
    material_id: int
    nombre: str
    categoria: str
    cantidad: float
    precio_unitario: float
    subtotal: float

class CotizacionCreate(BaseModel):
    """Schema para crear una cotización"""
    plano_id: int
    cliente_nombre: str
    cliente_email: EmailStr
    cliente_telefono: Optional[str] = None
    descripcion: Optional[str] = None
    materiales: List[MaterialCotizacion]
    subtotal: float
    iva: float
    total: float
    
    class Config:
        from_attributes = True

class CotizacionResponse(BaseModel):
    """Schema de respuesta para cotización"""
    id: int
    plano_id: int
    usuario_id: int
    cliente_nombre: str
    cliente_email: str
    cliente_telefono: Optional[str] = None
    descripcion: Optional[str] = None
    materiales: List[MaterialCotizacion]
    subtotal: float
    iva: float
    total: float
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True

class MedidasExtraidas(BaseModel):
    """Schema para medidas extraídas del plano"""
    area_total: Optional[float] = None  # m²
    perimetro_total: Optional[float] = None  # metros lineales
    num_paredes: int = 0
    num_ventanas: int = 0
    num_puertas: int = 0
    objetos: List[dict] = []  # Detalles de cada objeto
    
    class Config:
        from_attributes = True

