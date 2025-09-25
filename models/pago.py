from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from . import Base
import datetime

class Pago(Base):
    __tablename__ = "pagos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    suscripcion_id = Column(Integer, ForeignKey("suscripciones.id"))
    monto = Column(Float, nullable=False)
    moneda = Column(String, nullable=False)
    metodo = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    referencia_pasarela = Column(String)
    fecha_pago = Column(DateTime, default=datetime.datetime.utcnow)
    suscripcion = relationship("Suscripcion", back_populates="pagos")
