from models.usuario import Usuario
# back-fastapi/auth/dashboard.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/users/dashboard")
def dashboard(username: str = Depends(verify_token)):
    from database import get_db
    from fastapi import Request
    from models.usuario import Usuario
    from models.suscripcion import Suscripcion
    from models.membresia import Membresia
    from sqlalchemy.orm import Session
    db_gen = get_db()
    db: Session = next(db_gen)
    usuario = db.query(Usuario).filter(Usuario.correo == username).first()
    subscripcion = None
    plan = None
    if usuario:
        subscripcion = db.query(Suscripcion).filter(
            Suscripcion.usuario_id == usuario.id,
            Suscripcion.estado == 'activa'
        ).order_by(Suscripcion.fecha_fin.desc()).first()
        if subscripcion:
            membresia = db.query(Membresia).filter(Membresia.id == subscripcion.membresia_id).first()
            plan = membresia.nombre if membresia else None
    db.close()
    return {
        "subscripcion": bool(subscripcion),
        "plan": plan
    }
