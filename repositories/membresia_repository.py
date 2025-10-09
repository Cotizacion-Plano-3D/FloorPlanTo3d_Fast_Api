from models.membresia import Membresia
from sqlalchemy.orm import Session

def get_all_membresias(db: Session):
    return db.query(Membresia).all()

def get_membresia_by_id(db: Session, membresia_id: int):
    return db.query(Membresia).filter(Membresia.id == membresia_id).first()

def create_membresia(db: Session, membresia: Membresia):
    db.add(membresia)
    db.commit()
    db.refresh(membresia)
    return membresia

def update_membresia(db: Session, membresia: Membresia):
    db.commit()
    db.refresh(membresia)
    return membresia

def delete_membresia(db: Session, membresia: Membresia):
    db.delete(membresia)
    db.commit()
