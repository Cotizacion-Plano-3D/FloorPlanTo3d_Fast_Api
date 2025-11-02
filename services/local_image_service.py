"""
Servicio alternativo para guardar imágenes localmente (fallback si Google Drive falla)
"""

import os
import shutil
from datetime import datetime
from typing import Optional
from pathlib import Path

class LocalImageService:
    """Servicio para guardar imágenes localmente"""
    
    def __init__(self):
        # Directorio donde se guardarán las imágenes
        self.upload_dir = Path("uploads/textures")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
    def upload_image(self, file_content: bytes, filename: str, material_name: str) -> Optional[str]:
        """
        Guardar imagen localmente
        
        Args:
            file_content: Contenido del archivo en bytes
            filename: Nombre original del archivo
            material_name: Nombre del material
            
        Returns:
            URL relativa del archivo guardado
        """
        try:
            # Generar nombre único
            extension = Path(filename).suffix.lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = material_name.replace(" ", "_").lower()
            new_filename = f"texture_{safe_name}_{timestamp}{extension}"
            
            # Ruta completa del archivo
            file_path = self.upload_dir / new_filename
            
            # Guardar archivo
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Retornar URL relativa (para servir con FastAPI)
            relative_url = f"/uploads/textures/{new_filename}"
            
            print(f"✅ Imagen guardada localmente: {file_path}")
            print(f"🔗 URL: {relative_url}")
            
            return relative_url
            
        except Exception as e:
            print(f"❌ Error guardando imagen localmente: {e}")
            return None
    
    def delete_image(self, image_url: str) -> bool:
        """Eliminar imagen local"""
        try:
            # Extraer nombre del archivo de la URL
            filename = Path(image_url).name
            file_path = self.upload_dir / filename
            
            if file_path.exists():
                file_path.unlink()
                print(f"✅ Imagen eliminada: {file_path}")
                return True
            else:
                print(f"⚠️ Imagen no encontrada: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error eliminando imagen: {e}")
            return False

local_image_service = LocalImageService()
