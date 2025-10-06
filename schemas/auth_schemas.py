"""
Esquemas Pydantic para Autenticación
"""

from pydantic import BaseModel, Field, EmailStr

class LoginRequest(BaseModel):
    """Esquema para solicitud de login"""
    correo: EmailStr = Field(..., description="Correo electrónico del usuario", example="migracion@gmail.com")
    contrasena: str = Field(..., description="Contraseña del usuario", example="migracion")

class RegisterRequest(BaseModel):
    """Esquema para solicitud de registro"""
    correo: EmailStr = Field(..., description="Correo electrónico del usuario", example="migracion@gmail.com")
    contrasena: str = Field(..., min_length=6, description="Contraseña del usuario (mínimo 6 caracteres)", example="migracion")
    nombre: str = Field(..., description="Nombre completo del usuario", example="Juan Pérez")

class TokenResponse(BaseModel):
    """Esquema de respuesta para token de autenticación"""
    access_token: str = Field(..., description="Token JWT de acceso", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(..., description="Tipo de token", example="bearer")

class RegisterResponse(BaseModel):
    """Esquema de respuesta para registro"""
    message: str = Field(..., description="Mensaje de confirmación", example="Usuario juan.perez@email.com registrado con éxito")
    access_token: str = Field(..., description="Token JWT de acceso", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(..., description="Tipo de token", example="bearer")
