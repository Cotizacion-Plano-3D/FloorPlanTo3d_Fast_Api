"""
Esquemas Pydantic para Membresía
"""

from pydantic import BaseModel, Field
from typing import Optional

class MembresiaBase(BaseModel):
    """Esquema base para membresía"""
    nombre: str = Field(..., description="Nombre de la membresía", example="Plan Básico")
    precio: float = Field(..., gt=0, description="Precio de la membresía en USD", example=29.99)
    duracion: int = Field(..., gt=0, description="Duración de la membresía en días", example=30)
    descripcion: Optional[str] = Field(None, description="Descripción detallada de la membresía", 
                                     example="Acceso completo a todas las funciones básicas de conversión 3D")

class MembresiaCreate(MembresiaBase):
    """Esquema para crear una nueva membresía"""
    pass

class MembresiaResponse(MembresiaBase):
    """Esquema de respuesta para membresía"""
    id: int = Field(..., description="ID único de la membresía", example=1)
    stripe_price_id: Optional[str] = Field(None, description="ID del precio en Stripe", example="price_1234567890")
    
    class Config:
        from_attributes = True
