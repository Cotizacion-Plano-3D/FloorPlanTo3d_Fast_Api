"""
Repositorio para Cotización
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from models.cotizacion import Cotizacion
from schemas.cotizacion_schemas import CotizacionCreate

class CotizacionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, cotizacion_data: CotizacionCreate, usuario_id: int) -> Cotizacion:
        """Crear una nueva cotización"""
        cotizacion = Cotizacion(
            plano_id=cotizacion_data.plano_id,
            usuario_id=usuario_id,
            cliente_nombre=cotizacion_data.cliente_nombre,
            cliente_email=cotizacion_data.cliente_email,
            cliente_telefono=cotizacion_data.cliente_telefono,
            descripcion=cotizacion_data.descripcion,
            materiales=[m.dict() for m in cotizacion_data.materiales],
            subtotal=cotizacion_data.subtotal,
            iva=cotizacion_data.iva,
            total=cotizacion_data.total
        )
        
        self.db.add(cotizacion)
        self.db.commit()
        self.db.refresh(cotizacion)
        return cotizacion

    def get_by_id(self, cotizacion_id: int, usuario_id: int) -> Optional[Cotizacion]:
        """Obtener una cotización por ID"""
        return self.db.query(Cotizacion).filter(
            Cotizacion.id == cotizacion_id,
            Cotizacion.usuario_id == usuario_id
        ).first()

    def get_by_plano(self, plano_id: int, usuario_id: int) -> List[Cotizacion]:
        """Obtener todas las cotizaciones de un plano"""
        return self.db.query(Cotizacion).filter(
            Cotizacion.plano_id == plano_id,
            Cotizacion.usuario_id == usuario_id
        ).order_by(Cotizacion.fecha_creacion.desc()).all()

    def get_all_by_usuario(self, usuario_id: int, skip: int = 0, limit: int = 100) -> List[Cotizacion]:
        """Obtener todas las cotizaciones de un usuario"""
        return self.db.query(Cotizacion).filter(
            Cotizacion.usuario_id == usuario_id
        ).order_by(Cotizacion.fecha_creacion.desc()).offset(skip).limit(limit).all()

    def delete(self, cotizacion_id: int, usuario_id: int) -> bool:
        """Eliminar una cotización"""
        cotizacion = self.get_by_id(cotizacion_id, usuario_id)
        if not cotizacion:
            return False
        
        self.db.delete(cotizacion)
        self.db.commit()
        return True

