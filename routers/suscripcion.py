from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.suscripcion_service import (
    list_suscripciones, get_suscripcion, add_suscripcion, edit_suscripcion, remove_suscripcion,
    check_active_suscripcion
)
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/suscripciones", tags=["Suscripciones"])

class SuscripcionCreate(BaseModel):
    usuario_id: int
    membresia_id: int
    fecha_inicio: str
    fecha_fin: str
    estado: str

@router.get("/")
def get_suscripciones(db: Session = Depends(get_db)):
    return list_suscripciones(db)

@router.get("/{suscripcion_id}")
def get_suscripcion_by_id(suscripcion_id: int, db: Session = Depends(get_db)):
    suscripcion = get_suscripcion(db, suscripcion_id)
    if not suscripcion:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return suscripcion

@router.post("/")
def create_suscripcion(suscripcion: SuscripcionCreate, db: Session = Depends(get_db)):
    return add_suscripcion(db, suscripcion.dict())

@router.put("/{suscripcion_id}")
def update_suscripcion(suscripcion_id: int, suscripcion: SuscripcionCreate, db: Session = Depends(get_db)):
    updated = edit_suscripcion(db, suscripcion_id, suscripcion.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return updated

@router.delete("/{suscripcion_id}")
def delete_suscripcion(suscripcion_id: int, db: Session = Depends(get_db)):
    deleted = remove_suscripcion(db, suscripcion_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return {"detail": "Suscripción eliminada"}

@router.get("/activa/{usuario_id}")
def check_user_active_subscription(usuario_id: int, db: Session = Depends(get_db)):
    """
    Verifica si un usuario tiene una suscripción activa.
    
    Args:
        usuario_id: ID del usuario a verificar
        
    Returns:
        dict: Información sobre el estado de la suscripción
    """
    has_active_subscription = check_active_suscripcion(db, usuario_id)
    
    # Debug: obtener todas las suscripciones del usuario
    from models.suscripcion import Suscripcion
    from datetime import datetime
    all_suscripciones = db.query(Suscripcion).filter(Suscripcion.usuario_id == usuario_id).all()
    
    suscripciones_info = []
    for suscripcion in all_suscripciones:
        suscripciones_info.append({
            "id": suscripcion.id,
            "estado": suscripcion.estado,
            "fecha_inicio": suscripcion.fecha_inicio.isoformat() if suscripcion.fecha_inicio else None,
            "fecha_fin": suscripcion.fecha_fin.isoformat() if suscripcion.fecha_fin else None,
            "membresia_id": suscripcion.membresia_id
        })
    
    return {
        "usuario_id": usuario_id,
        "tiene_suscripcion_activa": has_active_subscription,
        "mensaje": "Usuario tiene suscripción activa" if has_active_subscription else "Usuario no tiene suscripción activa",
        "todas_las_suscripciones": suscripciones_info,
        "debug_info": {
            "fecha_actual": datetime.utcnow().isoformat(),
            "total_suscripciones": len(all_suscripciones)
        }
    }

@router.post("/crear-manual")
def crear_suscripcion_manual(
    usuario_id: int,
    membresia_id: int,
    db: Session = Depends(get_db)
):
    """
    Endpoint temporal para crear suscripciones manualmente
    (Solo para desarrollo/testing)
    """
    from models.usuario import Usuario
    from models.membresia import Membresia
    from models.suscripcion import Suscripcion
    from datetime import datetime, timedelta
    
    print(f"🔧 Creando suscripción manual para usuario {usuario_id}, membresía {membresia_id}")
    
    # Verificar que el usuario existe
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar que la membresía existe
    membresia = db.query(Membresia).filter(Membresia.id == membresia_id).first()
    if not membresia:
        raise HTTPException(status_code=404, detail="Membresía no encontrada")
    
    # Crear la suscripción
    nueva_suscripcion = Suscripcion(
        usuario_id=usuario_id,
        membresia_id=membresia_id,
        fecha_inicio=datetime.utcnow(),
        fecha_fin=datetime.utcnow() + timedelta(days=membresia.duracion),
        estado='activa'
    )
    
    db.add(nueva_suscripcion)
    db.commit()
    db.refresh(nueva_suscripcion)
    
    print(f"✅ Suscripción manual creada con ID: {nueva_suscripcion.id}")
    
    return {
        "message": "Suscripción creada exitosamente",
        "suscripcion_id": nueva_suscripcion.id,
        "usuario_id": usuario_id,
        "membresia_id": membresia_id,
        "fecha_inicio": nueva_suscripcion.fecha_inicio.isoformat(),
        "fecha_fin": nueva_suscripcion.fecha_fin.isoformat()
    }
