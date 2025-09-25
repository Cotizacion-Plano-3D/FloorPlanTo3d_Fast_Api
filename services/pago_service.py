from models.pago import Pago
from repositories.pago_repository import (
    get_all_pagos, get_pago_by_id, create_pago, update_pago, delete_pago
)
from sqlalchemy.orm import Session

def list_pagos(db: Session):
    return get_all_pagos(db)

def get_pago(db: Session, pago_id: int):
    return get_pago_by_id(db, pago_id)

def add_pago(db: Session, data: dict):
    pago = Pago(**data)
    return create_pago(db, pago)

def edit_pago(db: Session, pago_id: int, data: dict):
    pago = get_pago_by_id(db, pago_id)
    if not pago:
        return None
    for key, value in data.items():
        setattr(pago, key, value)
    return update_pago(db, pago)

def remove_pago(db: Session, pago_id: int):
    pago = get_pago_by_id(db, pago_id)
    if not pago:
        return None
    delete_pago(db, pago)
    return pago
