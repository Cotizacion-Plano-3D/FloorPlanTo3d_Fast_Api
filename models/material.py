from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class Material(Base):
    __tablename__ = "materiales"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio_base = Column(Float, nullable=False, default=0.0)
    unidad_medida = Column(String(20), nullable=False)  # m2, m3, unidad, kg, etc.
    imagen_url = Column(Text, nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="materiales")
    materiales_modelo3d = relationship("MaterialModelo3D", back_populates="material", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Material(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}')>"
