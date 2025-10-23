"""
Esquemas Pydantic para Plano
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from .modelo3d_schemas import Modelo3DResponse

class PlanoBase(BaseModel):
    """Esquema base para plano"""
    nombre: str = Field(..., description="Nombre del plano", example="Plano Casa Principal")
    formato: str = Field(default="image", description="Formato del archivo", example="jpg")
    tipo_plano: Optional[str] = Field(None, description="Tipo de plano", example="arquitectónico")
    descripcion: Optional[str] = Field(None, description="Descripción del plano", example="Plano de la casa principal")
    medidas_extraidas: Optional[Dict[str, Any]] = Field(None, description="Medidas extraídas del plano")

class PlanoCreate(PlanoBase):
    """Esquema para crear un nuevo plano"""
    pass

class PlanoUpdate(BaseModel):
    """Esquema para actualizar un plano"""
    nombre: Optional[str] = None
    tipo_plano: Optional[str] = None
    descripcion: Optional[str] = None
    medidas_extraidas: Optional[Dict[str, Any]] = None

class PlanoResponse(PlanoBase):
    """Esquema de respuesta para plano"""
    id: int = Field(..., description="ID único del plano", example=1)
    usuario_id: int = Field(..., description="ID del usuario propietario", example=1)
    url: Optional[str] = Field(None, description="URL del archivo", example="/uploads/plano1.jpg")
    estado: str = Field(..., description="Estado del plano", example="subido")
    fecha_subida: datetime = Field(..., description="Fecha de subida del plano")
    fecha_actualizacion: datetime = Field(..., description="Fecha de última actualización")
    modelo3d: Optional[Modelo3DResponse] = Field(None, description="Modelo 3D asociado si existe")
    
    class Config:
        from_attributes = True

class PlanoListResponse(BaseModel):
    """Esquema para lista de planos con paginación"""
    planos: list[PlanoResponse]
    total: int = Field(..., description="Total de planos")
    pagina: int = Field(..., description="Página actual")
    por_pagina: int = Field(..., description="Elementos por página")
    total_paginas: int = Field(..., description="Total de páginas")
