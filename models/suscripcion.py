from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class Suscripcion(Base):
    __tablename__ = "suscripciones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    membresia_id = Column(Integer, ForeignKey("membresias.id"))
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    estado = Column(String, nullable=False)
    usuario = relationship("Usuario", back_populates="suscripciones")
    membresia = relationship("Membresia", back_populates="suscripciones")
    pagos = relationship("Pago", back_populates="suscripcion")
