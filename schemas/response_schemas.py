"""
Esquemas Pydantic para Respuestas Generales
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any
from .usuario_schemas import UsuarioResponse
from .suscripcion_schemas import SuscripcionResponse
from .membresia_schemas import MembresiaResponse
from .pago_schemas import PagoResponse

class ErrorResponse(BaseModel):
    """Esquema para respuestas de error"""
    detail: str = Field(..., description="Mensaje de error detallado", example="Usuario o contraseña incorrectos")

class SuccessResponse(BaseModel):
    """Esquema para respuestas de éxito genéricas"""
    message: str = Field(..., description="Mensaje de confirmación", example="Operación realizada con éxito")
    data: Optional[Any] = Field(None, description="Datos de respuesta")

class DeleteResponse(BaseModel):
    """Esquema para respuestas de eliminación"""
    detail: str = Field(..., description="Mensaje de confirmación de eliminación", example="Membresía eliminada")

class DashboardResponse(BaseModel):
    """Esquema de respuesta para dashboard del usuario"""
    usuario: UsuarioResponse = Field(..., description="Información del usuario")
    suscripcion_activa: Optional[SuscripcionResponse] = Field(None, description="Suscripción activa del usuario")
    membresia: Optional[MembresiaResponse] = Field(None, description="Membresía asociada a la suscripción activa")
    pagos_recientes: List[PagoResponse] = Field(default_factory=list, description="Lista de pagos recientes")
