from models.usuario import Usuario
from sqlalchemy.orm import Session

def get_user_by_username(db: Session, username: str):
    return db.query(Usuario).filter(Usuario.correo == username).first()
