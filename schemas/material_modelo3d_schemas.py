from pydantic import BaseModel, Field, field_validator
from typing import Optional

# Schema para creación
class MaterialModelo3DCreate(BaseModel):
    modelo3d_id: int = Field(..., gt=0, description="ID del modelo 3D")
    material_id: int = Field(..., gt=0, description="ID del material")
    cantidad: float = Field(..., gt=0, description="Cantidad utilizada")
    unidad_medida: str = Field(..., min_length=1, max_length=20, description="Unidad de medida")
    precio_unitario: float = Field(..., ge=0, description="Precio unitario del material")
    
    @field_validator('unidad_medida')
    @classmethod
    def unidad_lowercase(cls, v):
        return v.lower().strip()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "modelo3d_id": 1,
                "material_id": 5,
                "cantidad": 45.5,
                "unidad_medida": "m2",
                "precio_unitario": 25.50
            }
        }
    }

# Schema para actualización
class MaterialModelo3DUpdate(BaseModel):
    cantidad: Optional[float] = Field(None, gt=0)
    precio_unitario: Optional[float] = Field(None, ge=0)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "cantidad": 50.0,
                "precio_unitario": 26.00
            }
        }
    }

# Schema para respuesta
class MaterialModelo3DResponse(BaseModel):
    id: int
    modelo3d_id: int
    material_id: int
    cantidad: float
    unidad_medida: str
    precio_unitario: float
    subtotal: float
    
    model_config = {
        "from_attributes": True
    }

# Schema para respuesta con detalles
class MaterialModelo3DConDetalles(MaterialModelo3DResponse):
    material: Optional[dict] = None
    
    model_config = {
        "from_attributes": True
    }

# Schema para resumen de costos
class ResumenCostosMateriales(BaseModel):
    total_materiales: int
    costo_total: float
    materiales: list[MaterialModelo3DConDetalles]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total_materiales": 5,
                "costo_total": 1250.75,
                "materiales": []
            }
        }
    }
