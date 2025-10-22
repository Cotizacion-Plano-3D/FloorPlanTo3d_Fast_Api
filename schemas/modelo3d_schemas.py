"""
Esquemas Pydantic para Modelo3D
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any

class Modelo3DBase(BaseModel):
    """Esquema base para modelo3d"""
    datos_json: Dict[str, Any] = Field(..., description="Datos JSON del modelo 3D")
    estado_renderizado: str = Field(default="generado", description="Estado del renderizado")

class Modelo3DCreate(Modelo3DBase):
    """Esquema para crear un nuevo modelo3d"""
    plano_id: int = Field(..., description="ID del plano asociado")

class Modelo3DResponse(Modelo3DBase):
    """Esquema de respuesta para modelo3d"""
    id: int = Field(..., description="ID único del modelo 3D", example=1)
    plano_id: int = Field(..., description="ID del plano asociado", example=1)
    fecha_generacion: datetime = Field(..., description="Fecha de generación del modelo")
    fecha_actualizacion: datetime = Field(..., description="Fecha de última actualización")
    
    class Config:
        from_attributes = True

class Modelo3DDataResponse(BaseModel):
    """Esquema para devolver solo los datos JSON del modelo 3D"""
    datos_json: Dict[str, Any] = Field(..., description="Datos JSON del modelo 3D para renderizado")
