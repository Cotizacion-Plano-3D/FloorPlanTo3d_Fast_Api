from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

# Schema para creación
class CategoriaCreate(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=50, description="Código único de la categoría")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la categoría")
    descripcion: Optional[str] = Field(None, description="Descripción detallada")
    imagen_url: Optional[str] = Field(None, description="URL de imagen representativa")
    
    @field_validator('codigo')
    @classmethod
    def codigo_uppercase(cls, v):
        return v.upper().strip()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "codigo": "PISOS",
                "nombre": "Pisos y Revestimientos",
                "descripcion": "Materiales para pisos, cerámicos, porcelanatos, etc.",
                "imagen_url": "https://example.com/categorias/pisos.jpg"
            }
        }
    }

# Schema para actualización
class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Pisos y Revestimientos Premium",
                "descripcion": "Materiales premium para pisos"
            }
        }
    }

# Schema para respuesta
class CategoriaResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    total_materiales: Optional[int] = 0
    
    model_config = {
        "from_attributes": True
    }

# Schema para listado con materiales
class CategoriaConMateriales(CategoriaResponse):
    materiales: list = []
    
    model_config = {
        "from_attributes": True
    }
