from models.suscripcion import Suscripcion
from sqlalchemy.orm import Session
from datetime import datetime

def get_all_suscripciones(db: Session):
    return db.query(Suscripcion).all()

def get_suscripcion_by_id(db: Session, suscripcion_id: int):
    return db.query(Suscripcion).filter(Suscripcion.id == suscripcion_id).first()

def create_suscripcion(db: Session, suscripcion: Suscripcion):
    db.add(suscripcion)
    db.commit()
    db.refresh(suscripcion)
    return suscripcion

def update_suscripcion(db: Session, suscripcion: Suscripcion):
    db.commit()
    db.refresh(suscripcion)
    return suscripcion

def delete_suscripcion(db: Session, suscripcion: Suscripcion):
    db.delete(suscripcion)
    db.commit()

def get_active_suscripcion_by_user_id(db: Session, usuario_id: int):
    """
    Obtiene la suscripción activa de un usuario.
    Una suscripción está activa si:
    - El estado es 'activa'
    - La fecha actual está entre fecha_inicio y fecha_fin
    """
    now = datetime.utcnow()
    return db.query(Suscripcion).filter(
        Suscripcion.usuario_id == usuario_id,
        Suscripcion.estado == 'activa',
        Suscripcion.fecha_inicio <= now,
        Suscripcion.fecha_fin >= now
    ).first()
