"""
Router para endpoints de Planos
"""

import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from middleware.auth_middleware import get_current_user
from services.plano_service import PlanoService
from schemas.plano_schemas import (
    PlanoCreate, PlanoUpdate, PlanoResponse, PlanoListResponse
)
from schemas.modelo3d_schemas import Modelo3DDataResponse, Modelo3DObjectsUpdate
from schemas.response_schemas import SuccessResponse, ErrorResponse

router = APIRouter(prefix="/planos", tags=["planos"])

# Ya no necesitamos guardar archivos localmente, se suben a Google Drive

@router.post("/", response_model=PlanoResponse)
async def create_plano(
    file: UploadFile = File(..., description="Archivo del plano"),
    nombre: str = Form(..., description="Nombre del plano"),
    formato: str = Form(default="image", description="Formato del archivo"),
    tipo_plano: Optional[str] = Form(None, description="Tipo de plano"),
    descripcion: Optional[str] = Form(None, description="Descripción del plano"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Subir un nuevo plano"""
    try:
        # Validar tipo de archivo
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.svg'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(allowed_extensions)}"
            )
        
        # Validar tamaño del archivo (10MB máximo)
        file.file.seek(0, 2)  # Ir al final del archivo
        file_size = file.file.tell()
        file.file.seek(0)  # Volver al inicio
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="El archivo es demasiado grande. Tamaño máximo: 10MB"
            )
        
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Crear plano
        plano_data = PlanoCreate(
            nombre=nombre,
            formato=formato,
            tipo_plano=tipo_plano,
            descripcion=descripcion
        )
        
        plano_service = PlanoService(db)
        plano = plano_service.create_plano(
            plano_data, 
            current_user.id, 
            file_content=file_content, 
            filename=file.filename
        )
        
        return plano
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir plano: {str(e)}")

@router.get("/", response_model=PlanoListResponse)
async def get_planos(
    skip: int = Query(0, ge=0, description="Número de elementos a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número de elementos a retornar"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener lista de planos del usuario"""
    plano_service = PlanoService(db)
    return plano_service.get_planos_usuario(current_user.id, skip, limit)

@router.get("/{plano_id}", response_model=PlanoResponse)
async def get_plano(
    plano_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # ← REQUIERE AUTENTICACIÓN
):
    """Obtener un plano específico"""
    plano_service = PlanoService(db)
    plano = plano_service.get_plano(plano_id, current_user.id)
    
    if not plano:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
    
    return plano

@router.put("/{plano_id}", response_model=PlanoResponse)
async def update_plano(
    plano_id: int,
    plano_data: PlanoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Actualizar un plano"""
    plano_service = PlanoService(db)
    plano = plano_service.update_plano(plano_id, current_user.id, plano_data)
    
    if not plano:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
    
    return plano

@router.delete("/{plano_id}", response_model=SuccessResponse)
async def delete_plano(
    plano_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar un plano"""
    plano_service = PlanoService(db)
    success = plano_service.delete_plano(plano_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
    
    return SuccessResponse(message="Plano eliminado exitosamente")

@router.post("/{plano_id}/convertir", response_model=SuccessResponse)
async def convertir_plano_a_3d(
    plano_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Convertir un plano a modelo 3D"""
    plano_service = PlanoService(db)
    result = plano_service.convertir_a_3d(plano_id, current_user.id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return SuccessResponse(message=result["message"])

@router.get("/{plano_id}/modelo3d", response_model=Modelo3DDataResponse)
async def get_modelo3d_data(
    plano_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener datos del modelo 3D para renderizado"""
    plano_service = PlanoService(db)
    modelo_data = plano_service.get_modelo3d_data(plano_id, current_user.id)
    
    if not modelo_data:
        raise HTTPException(status_code=404, detail="Modelo 3D no encontrado")
    
    return Modelo3DDataResponse(**modelo_data)

@router.get("/{plano_id}/render-3d")
async def render_3d_from_cache(
    plano_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Renderizar modelo 3D desde caché (datos_json).
    Este endpoint recupera los datos ya procesados sin volver a analizar la imagen,
    optimizando el tiempo de carga para visualizaciones posteriores.
    """
    plano_service = PlanoService(db)
    result = plano_service.render_modelo3d_from_cache(plano_id, current_user.id)
    
    if not result:
        raise HTTPException(
            status_code=404, 
            detail="Modelo 3D no encontrado o aún no ha sido procesado"
        )
    
    return result

@router.get("/{plano_id}/debug-image")
async def debug_plano_image(
    plano_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Debug endpoint para verificar el estado de la imagen del plano"""
    plano_service = PlanoService(db)
    plano = plano_service.get_plano(plano_id, current_user.id)
    
    if not plano:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
    
    if not plano.url:
        return {"error": "Plano no tiene URL de imagen"}
    
    # Extraer file_id de la URL
    if "drive.google.com/uc?export=view&id=" in plano.url:
        file_id = plano.url.split("id=")[1]
    else:
        return {"error": "URL no es de Google Drive", "url": plano.url}
    
    # Verificar información del archivo
    from services.google_drive_service import google_drive_service
    file_info = google_drive_service.get_file_info(file_id)
    
    # Intentar hacer público si no lo está
    is_public = google_drive_service.make_file_public(file_id)
    
    return {
        "plano_id": plano_id,
        "url": plano.url,
        "file_id": file_id,
        "file_info": file_info,
        "is_public": is_public,
        "direct_url": f"https://drive.google.com/uc?export=view&id={file_id}"
    }

@router.post("/make-all-public")
async def make_all_planos_public(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Hacer públicos todos los archivos de Google Drive del usuario"""
    plano_service = PlanoService(db)
    planos = plano_service.get_planos_usuario(current_user.id, 0, 1000)
    
    results = []
    from services.google_drive_service import google_drive_service
    
    for plano in planos.planos:
        if plano.url and "drive.google.com/uc?export=view&id=" in plano.url:
            file_id = plano.url.split("id=")[1]
            is_public = google_drive_service.make_file_public(file_id)
            results.append({
                "plano_id": plano.id,
                "file_id": file_id,
                "is_public": is_public,
                "url": plano.url
            })
    
    return {
        "message": f"Procesados {len(results)} planos",
        "results": results
    }

@router.get("/{plano_id}/image")
async def get_plano_image(
    plano_id: int,
    db: Session = Depends(get_db)
):
    """Obtener imagen del plano como proxy (sin autenticación para acceso público)"""
    plano_service = PlanoService(db)
    # Obtener plano sin verificar usuario (para acceso público a imágenes)
    plano = plano_service.get_plano_by_id(plano_id)
    
    if not plano:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
    
    if not plano.url:
        raise HTTPException(status_code=404, detail="Plano no tiene imagen")
    
    try:
        import requests
        
        # Descargar imagen de Google Drive
        response = requests.get(plano.url, timeout=30)
        response.raise_for_status()
        
        # Retornar imagen con headers apropiados
        from fastapi.responses import Response
        return Response(
            content=response.content,
            media_type=response.headers.get('content-type', 'image/jpeg'),
            headers={
                'Cache-Control': 'public, max-age=3600',
                'Content-Length': str(len(response.content)),
                'Access-Control-Allow-Origin': '*',  # Permitir acceso desde cualquier origen
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': '*',
            }
        )
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error descargando imagen: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")

@router.get("/{plano_id}/download")
async def download_plano(
    plano_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Descargar el archivo del plano"""
    plano_service = PlanoService(db)
    plano = plano_service.get_plano(plano_id, current_user.id)
    
    if not plano:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
    
    if not plano.url:
        raise HTTPException(status_code=404, detail="Plano no tiene archivo")
    
    try:
        import requests
        
        # Descargar archivo de Google Drive
        response = requests.get(plano.url, timeout=30)
        response.raise_for_status()
        
        # Determinar el tipo de archivo y extensión
        content_type = response.headers.get('content-type', 'application/octet-stream')
        file_extension = 'jpg'  # default
        if 'image/jpeg' in content_type:
            file_extension = 'jpg'
        elif 'image/png' in content_type:
            file_extension = 'png'
        elif 'image/svg' in content_type:
            file_extension = 'svg'
        elif 'application/pdf' in content_type:
            file_extension = 'pdf'
        
        # Retornar archivo con headers para descarga
        from fastapi.responses import Response
        return Response(
            content=response.content,
            media_type=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{plano.nombre}.{file_extension}"',
                'Content-Length': str(len(response.content)),
                'Cache-Control': 'no-cache'
            }
        )
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error descargando archivo: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

@router.put("/{plano_id}/modelo3d/objects", response_model=SuccessResponse)
async def update_modelo3d_objects(
    plano_id: int,
    update_data: Modelo3DObjectsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Actualizar dimensiones y posición de objetos específicos en el modelo 3D"""
    try:
        plano_service = PlanoService(db)
        
        # Convertir los objetos del schema a formato de diccionario
        objects_updates = []
        for obj_update in update_data.objects:
            update_dict = {
                "object_id": obj_update.object_id
            }
            
            if obj_update.width is not None:
                update_dict["width"] = obj_update.width
            if obj_update.height is not None:
                update_dict["height"] = obj_update.height
            if obj_update.depth is not None:
                update_dict["depth"] = obj_update.depth
            if obj_update.position is not None:
                update_dict["position"] = obj_update.position
            
            objects_updates.append(update_dict)
        
        result = plano_service.update_modelo3d_objects(plano_id, current_user.id, objects_updates)
        
        if not result:
            raise HTTPException(status_code=404, detail="Plano o modelo 3D no encontrado")
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Error al actualizar objetos"))
        
        return SuccessResponse(message=result.get("message", "Objetos actualizados exitosamente"))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar objetos: {str(e)}")