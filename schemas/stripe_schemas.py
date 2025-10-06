"""
Esquemas Pydantic para Stripe
"""

from pydantic import BaseModel, Field
from typing import Optional

class StripeWebhookRequest(BaseModel):
    """Esquema para webhook de Stripe"""
    type: str = Field(..., description="Tipo de evento de Stripe", example="payment_intent.succeeded")
    data: dict = Field(..., description="Datos del evento de Stripe")

class StripeCreateMembresiaRequest(BaseModel):
    """Esquema para crear membresía en Stripe"""
    nombre: str = Field(..., description="Nombre de la membresía", example="Plan Premium")
    precio: float = Field(..., gt=0, description="Precio mensual en USD", example=49.99)
    descripcion: Optional[str] = Field(None, description="Descripción de la membresía", example="Plan premium con todas las funciones")

class StripeCreateMembresiaResponse(BaseModel):
    """Esquema de respuesta para creación de membresía en Stripe"""
    membresia_id: int = Field(..., description="ID de la membresía creada", example=1)
    stripe_price_id: str = Field(..., description="ID del precio en Stripe", example="price_1234567890")
    message: str = Field(..., description="Mensaje de confirmación", example="Membresía creada exitosamente en Stripe")
