"""
Modelo de base de datos para Cotización
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base  # ✅ Cambiar de 'from database import Base' a 'from . import Base'
import datetime

class Cotizacion(Base):
    """Modelo de Cotización"""
    __tablename__ = "cotizaciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plano_id = Column(Integer, ForeignKey('plano.id', ondelete='CASCADE'), nullable=False, index=True)  # ✅ Cambiar 'planos.id' a 'plano.id'
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Datos del cliente
    cliente_nombre = Column(String(255), nullable=False)
    cliente_email = Column(String(255), nullable=False)
    cliente_telefono = Column(String(50), nullable=True)
    
    # Descripción del proyecto
    descripcion = Column(Text, nullable=True)
    
    # Materiales (JSON array) - Para PostgreSQL usar JSONB
    materiales = Column(JSON, nullable=False)  # En PostgreSQL podría ser JSONB
    
    # Totales
    subtotal = Column(Float, nullable=False, default=0.0)
    iva = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    
    # Timestamps - Usar formato consistente con otros modelos
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relaciones
    plano = relationship("Plano", back_populates="cotizaciones")
    usuario = relationship("Usuario", back_populates="cotizaciones")