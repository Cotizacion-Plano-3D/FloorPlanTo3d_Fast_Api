# routers/dashboard.py
from models.usuario import Usuario
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from middleware.auth_middleware import get_current_user
from schemas import DashboardResponse, UsuarioResponse, SuscripcionResponse, MembresiaResponse, PagoResponse
from typing import List, Optional

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    responses={
        401: {"description": "Token de autenticación inválido o expirado"},
        404: {"description": "Usuario no encontrado"}
    }
)

@router.get(
    "/",
    response_model=DashboardResponse,
    summary="Panel de control del usuario",
    description="""
    Obtiene información completa del dashboard del usuario autenticado.
    
    **Información incluida:**
    - Datos del usuario (nombre, correo, fecha de registro)
    - Suscripción activa (si existe)
    - Detalles de la membresía asociada
    - Historial de pagos recientes
    
    **Autenticación requerida:** Sí (JWT token)
    """,
    responses={
        200: {
            "description": "Dashboard obtenido exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "usuario": {
                            "id": 1,
                            "nombre": "Juan Pérez",
                            "correo": "juan.perez@email.com",
                            "fecha_creacion": "2024-01-15T10:30:00Z"
                        },
                        "suscripcion_activa": {
                            "id": 1,
                            "usuario_id": 1,
                            "membresia_id": 1,
                            "fecha_inicio": "2024-01-15T10:30:00Z",
                            "fecha_fin": "2024-02-15T10:30:00Z",
                            "estado": "activa"
                        },
                        "membresia": {
                            "id": 1,
                            "nombre": "Plan Básico",
                            "precio": 29.99,
                            "duracion": 30,
                            "descripcion": "Acceso completo a todas las funciones básicas"
                        },
                        "pagos_recientes": []
                    }
                }
            }
        }
    }
)
def dashboard(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Obtener dashboard del usuario
    
    Devuelve información completa del panel de control del usuario autenticado,
    incluyendo suscripción activa, membresía y historial de pagos.
    """
    from models.suscripcion import Suscripcion
    from models.membresia import Membresia
    from models.pago import Pago
    
    # Buscar suscripción activa
    suscripcion_activa = db.query(Suscripcion).filter(
        Suscripcion.usuario_id == current_user.id,
        Suscripcion.estado == 'activa'
    ).order_by(Suscripcion.fecha_fin.desc()).first()
    
    membresia = None
    if suscripcion_activa:
        membresia = db.query(Membresia).filter(
            Membresia.id == suscripcion_activa.membresia_id
        ).first()
    
    # Obtener pagos recientes (últimos 5)
    pagos_recientes = db.query(Pago).filter(
        Pago.suscripcion_id == suscripcion_activa.id
    ).order_by(Pago.fecha_pago.desc()).limit(5).all() if suscripcion_activa else []
    
    return DashboardResponse(
        usuario=UsuarioResponse.from_orm(current_user),
        suscripcion_activa=SuscripcionResponse.from_orm(suscripcion_activa) if suscripcion_activa else None,
        membresia=MembresiaResponse.from_orm(membresia) if membresia else None,
        pagos_recientes=[PagoResponse.from_orm(pago) for pago in pagos_recientes]
    )
