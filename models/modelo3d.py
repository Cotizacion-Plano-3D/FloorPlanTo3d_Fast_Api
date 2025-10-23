from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from . import Base
import datetime

class Modelo3D(Base):
    __tablename__ = "modelo3d"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plano_id = Column(Integer, ForeignKey("plano.id", ondelete="CASCADE"), nullable=False, unique=True)
    datos_json = Column(JSON, nullable=False)  # salida de Flask (Three.js-ready)
    estado_renderizado = Column(String(24), nullable=False, default="generado")
    fecha_generacion = Column(DateTime, default=datetime.datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relaciones
    plano = relationship("Plano", back_populates="modelo3d")
