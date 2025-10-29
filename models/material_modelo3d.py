from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class MaterialModelo3D(Base):
    __tablename__ = "materiales_modelo3d"
    
    id = Column(Integer, primary_key=True, index=True)
    modelo3d_id = Column(Integer, ForeignKey("modelo3d.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(Integer, ForeignKey("materiales.id", ondelete="CASCADE"), nullable=False)
    cantidad = Column(Float, nullable=False, default=0.0)
    unidad_medida = Column(String(20), nullable=False)
    precio_unitario = Column(Float, nullable=False, default=0.0)
    subtotal = Column(Float, nullable=False, default=0.0)
    
    # Relaciones
    modelo3d = relationship("Modelo3D", back_populates="materiales")
    material = relationship("Material", back_populates="materiales_modelo3d")
    
    def __repr__(self):
        return f"<MaterialModelo3D(id={self.id}, modelo3d_id={self.modelo3d_id}, material_id={self.material_id}, cantidad={self.cantidad})>"
