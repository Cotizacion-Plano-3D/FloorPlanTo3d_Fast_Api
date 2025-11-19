from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from . import Base
import datetime

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    contrasena = Column(String, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)
    suscripciones = relationship("Suscripcion", back_populates="usuario")
    planos = relationship("Plano", back_populates="usuario")
    cotizaciones = relationship("Cotizacion", back_populates="usuario")
