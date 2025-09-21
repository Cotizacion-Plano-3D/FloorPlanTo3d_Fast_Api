from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

# Usamos un conjunto en memoria para almacenar tokens inválidos
invalid_tokens = set()

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    """Este endpoint invalida el token."""
    # Añadir el token a la lista de tokens inválidos
    invalid_tokens.add(token)
    return {"message": "Sesión cerrada exitosamente."}
