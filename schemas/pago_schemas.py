"""
Esquemas Pydantic para Pago
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoPago(str, Enum):
    """Estados posibles de un pago"""
    pendiente = "pendiente"
    completado = "completado"
    fallido = "fallido"
    reembolsado = "reembolsado"

class PagoBase(BaseModel):
    """Esquema base para pago"""
    suscripcion_id: int = Field(..., description="ID de la suscripción", example=1)
    monto: float = Field(..., gt=0, description="Monto del pago en USD", example=29.99)
    fecha_pago: datetime = Field(..., description="Fecha del pago", example="2024-01-15T10:30:00Z")
    estado: EstadoPago = Field(..., description="Estado del pago", example="completado")

class PagoCreate(BaseModel):
    """Esquema para crear un nuevo pago"""
    suscripcion_id: int = Field(..., description="ID de la suscripción", example=1)
    monto: float = Field(..., gt=0, description="Monto del pago en USD", example=29.99)

class PagoResponse(PagoBase):
    """Esquema de respuesta para pago"""
    id: int = Field(..., description="ID único del pago", example=1)
    stripe_payment_intent_id: Optional[str] = Field(None, description="ID del payment intent en Stripe", example="pi_1234567890")
    
    class Config:
        from_attributes = True
