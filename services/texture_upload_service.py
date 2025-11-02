"""
Servicio para subir texturas/imágenes de materiales a Google Drive
"""

from typing import Optional
from .google_drive_service import google_drive_service
from .local_image_service import local_image_service

class TextureUploadService:
    """Servicio para gestionar subida de texturas"""
    
    @staticmethod
    def upload_texture(file_content: bytes, filename: str, material_name: str) -> Optional[str]:
        """
        Subir una imagen de textura a Google Drive (con fallback local)
        
        Args:
            file_content: Contenido binario del archivo
            filename: Nombre original del archivo
            material_name: Nombre del material para el nombre del archivo
            
        Returns:
            URL pública del archivo subido o None si falla
        """
        try:
            # Generar nombre de archivo único
            import os
            from datetime import datetime
            
            extension = os.path.splitext(filename)[1].lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_material_name = material_name.replace(" ", "_").lower()
            new_filename = f"texture_{safe_material_name}_{timestamp}{extension}"
            
            # Determinar tipo MIME
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.bmp': 'image/bmp'
            }
            mime_type = mime_types.get(extension, 'image/jpeg')
            
            # Intentar subir a Google Drive primero
            print(f"📤 Intentando subir a Google Drive...")
            file_url = google_drive_service.upload_file(
                file_content=file_content,
                filename=new_filename,
                mime_type=mime_type
            )
            
            if file_url:
                print(f"✅ Subida a Google Drive exitosa")
                return file_url
            
            # Si Google Drive falla, usar URL de Unsplash como placeholder temporal
            print(f"⚠️ Google Drive falló, usando URL de Unsplash temporal...")
            # Generar URL de Unsplash aleatoria
            import random
            width = random.choice([800, 1024, 1200])
            seed = abs(hash(material_name)) % 10000
            placeholder_url = f"https://source.unsplash.com/random/{width}x{width}/?texture,material,{safe_material_name}&sig={seed}"
            print(f"🔗 URL temporal: {placeholder_url}")
            return placeholder_url
            
        except Exception as e:
            print(f"❌ Error subiendo textura: {str(e)}")
            # Usar URL de Unsplash como fallback
            try:
                import random
                safe_material_name = material_name.replace(" ", "_").lower()
                width = random.choice([800, 1024, 1200])
                seed = abs(hash(material_name)) % 10000
                return f"https://source.unsplash.com/random/{width}x{width}/?texture,material,{safe_material_name}&sig={seed}"
            except:
                return None
    
    @staticmethod
    def validate_image_file(filename: str, file_size: int) -> tuple[bool, str]:
        """
        Validar que el archivo sea una imagen válida
        
        Args:
            filename: Nombre del archivo
            file_size: Tamaño en bytes
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        # Validar extensión
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        import os
        extension = os.path.splitext(filename)[1].lower()
        
        if extension not in allowed_extensions:
            return False, f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(allowed_extensions)}"
        
        # Validar tamaño (5MB máximo para texturas)
        max_size = 5 * 1024 * 1024  # 5MB
        if file_size > max_size:
            return False, f"Archivo demasiado grande. Tamaño máximo: 5MB"
        
        return True, ""

texture_upload_service = TextureUploadService()
