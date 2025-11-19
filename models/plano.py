from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from . import Base
import datetime

class Plano(Base):
    __tablename__ = "plano"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(255), nullable=False)
    url = Column(Text)  # ubicación del archivo (S3/local)
    formato = Column(String(32), default="image")  # jpg|png|pdf|image|svg, etc.
    tipo_plano = Column(String(64))  # arquitectónico, mano_alzada, etc.
    descripcion = Column(Text)
    medidas_extraidas = Column(JSON)  # metadatos/medidas detectadas (opcional)
    estado = Column(String(24), nullable=False, default="subido")
    fecha_subida = Column(DateTime, default=datetime.datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="planos")
    modelo3d = relationship("Modelo3D", back_populates="plano", uselist=False, cascade="all, delete-orphan")
    cotizaciones = relationship("Cotizacion", back_populates="plano", cascade="all, delete-orphan")
