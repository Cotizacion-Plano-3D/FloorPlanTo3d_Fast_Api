from models.pago import Pago
from sqlalchemy.orm import Session

def get_all_pagos(db: Session):
    return db.query(Pago).all()

def get_pago_by_id(db: Session, pago_id: int):
    return db.query(Pago).filter(Pago.id == pago_id).first()

def create_pago(db: Session, pago: Pago):
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago

def update_pago(db: Session, pago: Pago):
    db.commit()
    db.refresh(pago)
    return pago

def delete_pago(db: Session, pago: Pago):
    db.delete(pago)
    db.commit()
