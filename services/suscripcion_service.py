from models.suscripcion import Suscripcion
from repositories.suscripcion_repository import (
    get_all_suscripciones, get_suscripcion_by_id, create_suscripcion, update_suscripcion, delete_suscripcion
)
from sqlalchemy.orm import Session

def list_suscripciones(db: Session):
    return get_all_suscripciones(db)

def get_suscripcion(db: Session, suscripcion_id: int):
    return get_suscripcion_by_id(db, suscripcion_id)

def add_suscripcion(db: Session, data: dict):
    suscripcion = Suscripcion(**data)
    return create_suscripcion(db, suscripcion)

def edit_suscripcion(db: Session, suscripcion_id: int, data: dict):
    suscripcion = get_suscripcion_by_id(db, suscripcion_id)
    if not suscripcion:
        return None
    for key, value in data.items():
        setattr(suscripcion, key, value)
    return update_suscripcion(db, suscripcion)

def remove_suscripcion(db: Session, suscripcion_id: int):
    suscripcion = get_suscripcion_by_id(db, suscripcion_id)
    if not suscripcion:
        return None
    delete_suscripcion(db, suscripcion)
    return suscripcion
