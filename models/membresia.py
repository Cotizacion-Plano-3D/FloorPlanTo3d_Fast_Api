from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from . import Base

class Membresia(Base):
    __tablename__ = "membresias"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    duracion = Column(Integer, nullable=False)  # en días
    descripcion = Column(String)
    suscripciones = relationship("Suscripcion", back_populates="membresia")
