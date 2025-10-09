from models.membresia import Membresia
from repositories.membresia_repository import (
    get_all_membresias, get_membresia_by_id, create_membresia, update_membresia, delete_membresia
)
from sqlalchemy.orm import Session

def list_membresias(db: Session):
    return get_all_membresias(db)

def get_membresia(db: Session, membresia_id: int):
    return get_membresia_by_id(db, membresia_id)

def add_membresia(db: Session, data: dict):
    membresia = Membresia(**data)
    return create_membresia(db, membresia)

def edit_membresia(db: Session, membresia_id: int, data: dict):
    membresia = get_membresia_by_id(db, membresia_id)
    if not membresia:
        return None
    for key, value in data.items():
        setattr(membresia, key, value)
    return update_membresia(db, membresia)

def remove_membresia(db: Session, membresia_id: int):
    membresia = get_membresia_by_id(db, membresia_id)
    if not membresia:
        return None
    delete_membresia(db, membresia)
    return membresia
