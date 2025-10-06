"""
Esquemas Pydantic para Suscripción
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoSuscripcion(str, Enum):
    """Estados posibles de una suscripción"""
    activa = "activa"
    cancelada = "cancelada"
    expirada = "expirada"
    pendiente = "pendiente"

class SuscripcionBase(BaseModel):
    """Esquema base para suscripción"""
    usuario_id: int = Field(..., description="ID del usuario", example=1)
    membresia_id: int = Field(..., description="ID de la membresía", example=1)
    fecha_inicio: datetime = Field(..., description="Fecha de inicio de la suscripción", example="2024-01-15T10:30:00Z")
    fecha_fin: datetime = Field(..., description="Fecha de fin de la suscripción", example="2024-02-15T10:30:00Z")
    estado: EstadoSuscripcion = Field(..., description="Estado actual de la suscripción", example="activa")

class SuscripcionCreate(BaseModel):
    """Esquema para crear una nueva suscripción"""
    usuario_id: int = Field(..., description="ID del usuario", example=1)
    membresia_id: int = Field(..., description="ID de la membresía", example=1)

class SuscripcionResponse(SuscripcionBase):
    """Esquema de respuesta para suscripción"""
    id: int = Field(..., description="ID único de la suscripción", example=1)
    stripe_subscription_id: Optional[str] = Field(None, description="ID de la suscripción en Stripe", example="sub_1234567890")
    
    class Config:
        from_attributes = True
