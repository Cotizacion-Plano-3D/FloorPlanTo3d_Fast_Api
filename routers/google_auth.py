# routers/google_auth.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow  # Import correcto para aplicación web
from config import settings

router = APIRouter(prefix="/auth/google", tags=["google-auth"])

@router.get("/login")
async def google_login():
    """Iniciar flujo de autenticación con Google"""
    try:
        # Crear flujo OAuth2 para aplicación web
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CREDENTIALS_PATH,
            ['https://www.googleapis.com/auth/drive.file'],
            redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI
        )
        
        # Obtener URL de autorización
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error iniciando autenticación: {str(e)}")

@router.get("/callback")
async def google_callback(code: str = None):
    """Manejar callback de Google OAuth"""
    try:
        if not code:
            raise HTTPException(status_code=400, detail="Código de autorización no recibido")
        
        # Intercambiar código por token
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CREDENTIALS_PATH,
            ['https://www.googleapis.com/auth/drive.file'],
            redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI
        )
        
        flow.fetch_token(code=code)
        
        # Guardar credenciales
        credentials = flow.credentials
        with open('token.json', 'w') as token_file:
            token_file.write(credentials.to_json())
        
        return {"message": "Autenticación exitosa", "status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en callback: {str(e)}")