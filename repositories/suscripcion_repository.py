from models.suscripcion import Suscripcion
from sqlalchemy.orm import Session

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
