"""
Esquemas Pydantic para Usuario
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class UsuarioBase(BaseModel):
    """Esquema base para usuario"""
    nombre: str = Field(..., description="Nombre completo del usuario", example="Juan Pérez")
    correo: EmailStr = Field(..., description="Correo electrónico del usuario", example="juan.perez@email.com")

class UsuarioCreate(UsuarioBase):
    """Esquema para crear un nuevo usuario"""
    contrasena: str = Field(..., min_length=6, description="Contraseña del usuario (mínimo 6 caracteres)", example="miPassword123")

class UsuarioResponse(UsuarioBase):
    """Esquema de respuesta para usuario"""
    id: int = Field(..., description="ID único del usuario", example=1)
    fecha_creacion: datetime = Field(..., description="Fecha de creación del usuario", example="2024-01-15T10:30:00Z")
    
    class Config:
        from_attributes = True
