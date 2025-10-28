from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

# Schema para creación
class MaterialCreate(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=50, description="Código único del material")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del material")
    descripcion: Optional[str] = Field(None, description="Descripción detallada")
    precio_base: float = Field(..., ge=0, description="Precio base del material")
    unidad_medida: str = Field(..., min_length=1, max_length=20, description="Unidad de medida (m2, m3, unidad, kg, etc.)")
    imagen_url: Optional[str] = Field(None, description="URL de imagen del material")
    categoria_id: int = Field(..., gt=0, description="ID de la categoría")
    
    @field_validator('codigo')
    @classmethod
    def codigo_uppercase(cls, v):
        return v.upper().strip()
    
    @field_validator('unidad_medida')
    @classmethod
    def unidad_lowercase(cls, v):
        return v.lower().strip()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "codigo": "CER-001",
                "nombre": "Cerámica Blanca 30x30",
                "descripcion": "Cerámica esmaltada color blanco brillante",
                "precio_base": 25.50,
                "unidad_medida": "m2",
                "imagen_url": "https://example.com/materiales/ceramica-001.jpg",
                "categoria_id": 1
            }
        }
    }

# Schema para actualización
class MaterialUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio_base: Optional[float] = Field(None, ge=0)
    unidad_medida: Optional[str] = Field(None, min_length=1, max_length=20)
    imagen_url: Optional[str] = None
    categoria_id: Optional[int] = Field(None, gt=0)
    
    @field_validator('unidad_medida')
    @classmethod
    def unidad_lowercase(cls, v):
        if v:
            return v.lower().strip()
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Cerámica Blanca Premium 30x30",
                "precio_base": 28.00
            }
        }
    }

# Schema para respuesta
class MaterialResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float
    unidad_medida: str
    imagen_url: Optional[str] = None
    categoria_id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    model_config = {
        "from_attributes": True
    }

# Schema para respuesta con categoría
class MaterialConCategoria(MaterialResponse):
    categoria: Optional[dict] = None
    
    model_config = {
        "from_attributes": True
    }
