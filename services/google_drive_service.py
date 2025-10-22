"""
Servicio real para manejar archivos en Google Drive
"""

import os
import json
import io
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from config import settings

class GoogleDriveService:
    def __init__(self):
        self.folder_id = settings.GOOGLE_DRIVE_FOLDER_ID
        self.credentials_path = settings.GOOGLE_CREDENTIALS_PATH
        self.redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
        
        # Scopes necesarios para Google Drive
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        
        self.service = None
        self.credentials = None
        
    def authenticate(self):
        """Autenticación real con Google Drive"""
        try:
            # Cargar credenciales existentes
            if os.path.exists('token.json'):
                self.credentials = Credentials.from_authorized_user_file('token.json', self.SCOPES)
            
            # Si no hay credenciales válidas, autenticar
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    # Crear flujo OAuth2
                    flow = Flow.from_client_secrets_file(
                        self.credentials_path, 
                        self.SCOPES,
                        redirect_uri=self.redirect_uri
                    )
                    # Para aplicación web, usar puerto específico
                    self.credentials = flow.run_local_server(port=8000)
                
                # Guardar credenciales para uso futuro
                with open('token.json', 'w') as token:
                    token.write(self.credentials.to_json())
            
            # Crear servicio de Google Drive
            self.service = build('drive', 'v3', credentials=self.credentials)
            print("✅ Autenticación con Google Drive exitosa")
            return True
            
        except Exception as e:
            print(f"❌ Error en autenticación: {e}")
            return False
    
    def upload_file(self, file_content: bytes, filename: str, mime_type: str = 'image/jpeg') -> Optional[str]:
        """
        Subir archivo real a Google Drive
        
        Args:
            file_content: Contenido del archivo en bytes
            filename: Nombre del archivo
            mime_type: Tipo MIME del archivo
            
        Returns:
            URL del archivo en Google Drive
        """
        try:
            # Autenticar si no está autenticado
            if not self.service:
                if not self.authenticate():
                    return None
            
            # Crear metadatos del archivo
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id]  # Subir al folder específico
            }
            
            # Crear objeto de media
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=mime_type,
                resumable=True
            )
            
            # Subir archivo
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink'
            ).execute()
            
            # Obtener URL de visualización
            file_id = file.get('id')
            web_view_link = file.get('webViewLink')
            
            # Hacer el archivo público para que sea accesible
            try:
                self.service.permissions().create(
                    fileId=file_id,
                    body={'role': 'reader', 'type': 'anyone'}
                ).execute()
                print(f"✅ Archivo {file_id} hecho público")
            except Exception as e:
                print(f"⚠️ No se pudo hacer público el archivo: {e}")
            
            # Generar URL de descarga directa
            download_url = f"https://drive.google.com/uc?export=view&id={file_id}"
            
            print(f"✅ Archivo subido exitosamente: {filename}")
            print(f"🔗 URL: {download_url}")
            
            return download_url
            
        except Exception as e:
            print(f"❌ Error subiendo archivo: {e}")
            return None
    
    def delete_file(self, file_id: str) -> bool:
        """Eliminar archivo de Google Drive"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            self.service.files().delete(fileId=file_id).execute()
            print(f"✅ Archivo eliminado: {file_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error eliminando archivo: {e}")
            return False
    
    def get_file_info(self, file_id: str) -> Optional[dict]:
        """Obtener información de archivo"""
        try:
            if not self.service:
                if not self.authenticate():
                    return None
            
            file = self.service.files().get(fileId=file_id).execute()
            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'size': file.get('size'),
                'mimeType': file.get('mimeType'),
                'webViewLink': file.get('webViewLink')
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo info de archivo: {e}")
            return None
    
    def make_file_public(self, file_id: str) -> bool:
        """Hacer un archivo público para que sea accesible"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            # Verificar si ya es público
            permissions = self.service.permissions().list(fileId=file_id).execute()
            for permission in permissions.get('items', []):
                if permission.get('type') == 'anyone' and permission.get('role') == 'reader':
                    print(f"✅ Archivo {file_id} ya es público")
                    return True
            
            # Hacer público
            self.service.permissions().create(
                fileId=file_id,
                body={'role': 'reader', 'type': 'anyone'}
            ).execute()
            print(f"✅ Archivo {file_id} hecho público")
            return True
            
        except Exception as e:
            print(f"❌ Error haciendo público el archivo {file_id}: {e}")
            return False

# Instancia global del servicio
google_drive_service = GoogleDriveService()