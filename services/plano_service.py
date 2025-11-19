"""
Servicio de negocio para Plano
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from repositories.plano_repository import PlanoRepository
from repositories.modelo3d_repository import Modelo3DRepository
from schemas.plano_schemas import PlanoCreate, PlanoUpdate, PlanoResponse, PlanoListResponse
from schemas.modelo3d_schemas import Modelo3DResponse
import requests
import os
from config import settings
from .google_drive_service import google_drive_service

class PlanoService:
    def __init__(self, db: Session):
        self.db = db
        self.plano_repo = PlanoRepository(db)
        self.modelo3d_repo = Modelo3DRepository(db)

    def create_plano(self, plano_data: PlanoCreate, usuario_id: int, file_content: bytes = None, filename: str = None) -> PlanoResponse:
        """Crear un nuevo plano con verificación previa"""
        if not file_content or not filename:
            raise Exception("Archivo requerido para crear plano")
        
        # PASO 1: Verificar que es un plano válido con FloorPlanTo3D-API
        print(f"🔍 Verificando que el archivo es un plano válido...")
        
        try:
            # Llamar a FloorPlanTo3D-API para verificar que es un plano
            flask_url = settings.FLOORPLAN_API_URL
            response = requests.post(
                f"{flask_url}/convert",
                files={"file": (filename, file_content, "image/png")},
                params={"format": "threejs"},
                timeout=60  # 60 segundos para verificación
            )
            
            # Manejar diferentes tipos de errores
            if response.status_code != 200:
                print(f"❌ Error del API: {response.status_code}")
                print(f"📄 Respuesta: {response.text[:200]}...")
                
                # Si es error 500, probablemente no es un plano válido
                if response.status_code == 500:
                    raise Exception("El archivo no es un plano arquitectónico válido. El sistema no pudo procesar la imagen.")
                elif response.status_code == 400:
                    raise Exception("El archivo no es un plano arquitectónico válido. Formato de imagen no soportado.")
                elif response.status_code == 422:
                    raise Exception("El archivo no es un plano arquitectónico válido. Imagen corrupta o inválida.")
                else:
                    raise Exception(f"El archivo no es un plano válido. Error del sistema: {response.status_code}")
            
            # Verificar que la respuesta contiene datos de plano
            try:
                verification_data = response.json()
            except ValueError:
                raise Exception("El archivo no es un plano arquitectónico válido. Respuesta inválida del sistema.")
            
            if not verification_data.get('objects') or len(verification_data.get('objects', [])) == 0:
                raise Exception("El archivo no contiene elementos de plano reconocibles (paredes, puertas, ventanas)")
            
            print(f"✅ Verificación exitosa: {len(verification_data.get('objects', []))} objetos detectados")
            
            # 🔍 EXTRAER MEDIDAS del plano
            medidas_extraidas = self._extract_measurements(verification_data)
            print(f"📏 Medidas extraídas: {medidas_extraidas}")
            
        except requests.exceptions.Timeout:
            raise Exception("El archivo no es un plano arquitectónico válido. Tiempo de procesamiento excedido.")
        except requests.exceptions.ConnectionError:
            raise Exception("Error de conexión con el servicio de verificación. Intenta nuevamente.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error de conexión con el servicio de verificación: {str(e)}")
        except Exception as e:
            # Si ya es un mensaje amigable, re-lanzarlo
            if "no es un plano" in str(e).lower() or "no contiene elementos" in str(e).lower():
                raise e
            else:
                raise Exception(f"El archivo no es un plano arquitectónico válido: {str(e)}")
        
        # PASO 2: Si la verificación es exitosa, subir a Google Drive
        file_url = None
        try:
            # Determinar el tipo MIME basado en la extensión del archivo
            mime_type = 'image/jpeg'  # Por defecto
            if filename.lower().endswith('.png'):
                mime_type = 'image/png'
            elif filename.lower().endswith('.gif'):
                mime_type = 'image/gif'
            elif filename.lower().endswith('.webp'):
                mime_type = 'image/webp'
            
            print(f"📤 Subiendo archivo verificado a Google Drive...")
            
            # Subir archivo a Google Drive
            file_url = google_drive_service.upload_file(
                file_content=file_content,
                filename=filename,
                mime_type=mime_type
            )
            
            if not file_url:
                raise Exception("Error al subir archivo a Google Drive")
            
            print(f"✅ Archivo subido exitosamente a Google Drive")
                
        except Exception as e:
            print(f"❌ Error subiendo archivo a Google Drive: {e}")
            raise Exception(f"Error al subir archivo: {str(e)}")
        
        # PASO 3: Crear registro en BD con estado 'completado' (ya verificado y convertido)
        # Agregar medidas extraídas al plano_data
        plano_data_with_measures = PlanoCreate(
            nombre=plano_data.nombre,
            formato=plano_data.formato,
            tipo_plano=plano_data.tipo_plano,
            descripcion=plano_data.descripcion,
            medidas_extraidas=medidas_extraidas
        )
        plano = self.plano_repo.create(plano_data_with_measures, usuario_id, file_url)
        
        # Actualizar estado a completado ya que ya fue verificado y convertido
        self.plano_repo.update_estado(plano.id, usuario_id, "completado")
        
        # PASO 4: Guardar datos del modelo 3D directamente
        try:
            self.modelo3d_repo.update(plano.id, verification_data, "generado")
            print(f"✅ Modelo 3D guardado en base de datos")
        except Exception as e:
            print(f"⚠️ Error guardando modelo 3D: {e}")
            # No fallar por esto, el plano ya está creado
        
        return PlanoResponse.from_orm(plano)

    def get_plano(self, plano_id: int, usuario_id: int) -> Optional[PlanoResponse]:
        """Obtener un plano por ID"""
        plano = self.plano_repo.get_by_id(plano_id, usuario_id)
        if not plano:
            return None
        
        # Cargar modelo3d si existe
        modelo3d = self.modelo3d_repo.get_by_plano_id(plano_id)
        plano_dict = PlanoResponse.from_orm(plano).dict()
        
        if modelo3d:
            plano_dict['modelo3d'] = Modelo3DResponse.from_orm(modelo3d)
        
        return PlanoResponse(**plano_dict)

    def get_plano_by_id(self, plano_id: int) -> Optional[PlanoResponse]:
        """Obtener un plano por ID sin verificar usuario (para acceso público)"""
        plano = self.plano_repo.get_by_id_only(plano_id)
        if not plano:
            return None
        
        return PlanoResponse.from_orm(plano)

    def get_planos_usuario(self, usuario_id: int, skip: int = 0, limit: int = 100) -> PlanoListResponse:
        """Obtener lista paginada de planos del usuario"""
        planos = self.plano_repo.get_all_by_usuario(usuario_id, skip, limit)
        total = self.plano_repo.count_by_usuario(usuario_id)
        
        # Convertir a response con modelo3d incluido
        planos_response = []
        for plano in planos:
            modelo3d = self.modelo3d_repo.get_by_plano_id(plano.id)
            plano_dict = PlanoResponse.from_orm(plano).dict()
            
            if modelo3d:
                plano_dict['modelo3d'] = Modelo3DResponse.from_orm(modelo3d)
            
            planos_response.append(PlanoResponse(**plano_dict))
        
        total_paginas = (total + limit - 1) // limit
        pagina_actual = (skip // limit) + 1
        
        return PlanoListResponse(
            planos=planos_response,
            total=total,
            pagina=pagina_actual,
            por_pagina=limit,
            total_paginas=total_paginas
        )

    def update_plano(self, plano_id: int, usuario_id: int, plano_data: PlanoUpdate) -> Optional[PlanoResponse]:
        """Actualizar un plano"""
        plano = self.plano_repo.update(plano_id, usuario_id, plano_data)
        if not plano:
            return None
        
        return PlanoResponse.from_orm(plano)

    def delete_plano(self, plano_id: int, usuario_id: int) -> bool:
        """Eliminar un plano"""
        return self.plano_repo.delete(plano_id, usuario_id)

    def convertir_a_3d(self, plano_id: int, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Convertir un plano a 3D usando el servicio Flask"""
        # Verificar que el plano existe y pertenece al usuario
        plano = self.plano_repo.get_by_id(plano_id, usuario_id)
        if not plano:
            return None
        
        # Verificar que el plano tiene URL de archivo
        if not plano.url:
            return None
        
        try:
            # Cambiar estado a procesando
            self.plano_repo.update_estado(plano_id, usuario_id, "procesando")
            
            # Para URLs simuladas de Google Drive, usar archivo de prueba
            file_content = None
            if plano.url.startswith('http') and 'TEMP_' in plano.url:
                # Usar archivo de prueba para URLs simuladas
                print("Usando archivo de prueba para URL simulada")
                with open("test_image.png", "rb") as f:
                    file_content = f.read()
            elif plano.url.startswith('http'):
                # Descargar archivo real de Google Drive
                file_response = requests.get(plano.url, timeout=30)
                if file_response.status_code == 200:
                    file_content = file_response.content
                else:
                    raise Exception(f"No se pudo descargar el archivo de Google Drive: {file_response.status_code}")
            else:
                # Archivo local
                with open(plano.url, "rb") as f:
                    file_content = f.read()
            
            # Llamar al servicio Flask para conversión real
            flask_url = settings.FLOORPLAN_API_URL
            datos_json = None
            
            try:
                print(f"🚀 Llamando a FloorPlanTo3D-API: {flask_url}/convert?format=threejs")
                response = requests.post(
                    f"{flask_url}/convert",
                    files={"file": (plano.nombre, file_content, "image/png")},
                    params={"format": "threejs"},  # Formato optimizado para Three.js
                    timeout=120  # 120 segundos para procesamiento
                )
                
                if response.status_code == 200:
                    datos_json = response.json()
                    print("✅ Conversión exitosa desde FloorPlanTo3D-API")
                    print(f"📊 Datos recibidos: {len(datos_json.get('objects', []))} objetos detectados")
                else:
                    error_msg = f"FloorPlanTo3D-API retornó status {response.status_code}"
                    print(f"❌ {error_msg}")
                    raise Exception(error_msg)
                    
            except requests.exceptions.RequestException as req_error:
                error_msg = f"No se puede conectar a FloorPlanTo3D-API: {str(req_error)}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            # Guardar modelo3d
            modelo3d = self.modelo3d_repo.update(plano_id, datos_json, "generado")
            
            # Cambiar estado a completado
            self.plano_repo.update_estado(plano_id, usuario_id, "completado")
            
            return {
                "success": True,
                "modelo3d": Modelo3DResponse.from_orm(modelo3d),
                "message": "Plano convertido exitosamente"
            }
                
        except requests.exceptions.RequestException as e:
            # Error de conexión
            self.plano_repo.update_estado(plano_id, usuario_id, "error")
            return {
                "success": False,
                "error": f"Error de conexión con servicio de conversión: {str(e)}"
            }
        except Exception as e:
            # Error general
            self.plano_repo.update_estado(plano_id, usuario_id, "error")
            error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            return {
                "success": False,
                "error": f"Error interno: {error_msg}"
            }

    def get_modelo3d_data(self, plano_id: int, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtener datos JSON del modelo 3D para renderizado"""
        modelo3d = self.modelo3d_repo.get_by_plano_id_and_usuario(plano_id, usuario_id)
        if not modelo3d:
            return None
        
        return {
            "datos_json": modelo3d.datos_json
        }
    
    def render_modelo3d_from_cache(self, plano_id: int, usuario_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener modelo 3D desde caché (datos_json) para re-renderizado rápido.
        No requiere volver a procesar la imagen, optimizando tiempos de carga.
        """
        # Obtener el modelo3d de la base de datos
        modelo3d = self.modelo3d_repo.get_by_plano_id_and_usuario(plano_id, usuario_id)
        if not modelo3d:
            return None
        
        # Verificar que tenga datos_json
        if not modelo3d.datos_json:
            return None
        
        # Retornar los datos directamente - ya están en formato Three.js
        return {
            "success": True,
            "datos_json": modelo3d.datos_json,
            "from_cache": True,
            "plano_id": plano_id,
            "fecha_generacion": modelo3d.fecha_generacion.isoformat() if modelo3d.fecha_generacion else None
        }
    
    def update_modelo3d_objects(self, plano_id: int, usuario_id: int, objects_updates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Actualizar dimensiones y posición de objetos específicos en el modelo 3D.
        
        Args:
            plano_id: ID del plano
            usuario_id: ID del usuario (para verificación de permisos)
            objects_updates: Lista de diccionarios con actualizaciones de objetos
                Cada diccionario debe tener:
                - object_id: ID del objeto (string)
                - width, height, depth: Dimensiones opcionales
                - position: Diccionario con x, y, z opcionales
        
        Returns:
            Diccionario con success, message y datos_json actualizado
        """
        # Verificar que el plano existe y pertenece al usuario
        plano = self.plano_repo.get_by_id(plano_id, usuario_id)
        if not plano:
            return None
        
        # Obtener el modelo3d
        modelo3d = self.modelo3d_repo.get_by_plano_id_and_usuario(plano_id, usuario_id)
        if not modelo3d:
            return None
        
        # Obtener datos_json actual
        datos_json = modelo3d.datos_json.copy() if modelo3d.datos_json else {}
        
        # Obtener lista de objetos
        objects = datos_json.get('objects', [])
        if not objects:
            return {
                "success": False,
                "error": "No se encontraron objetos en el modelo 3D"
            }
        
        # Crear un diccionario para acceso rápido por ID
        objects_dict = {str(obj.get('id')): obj for obj in objects}
        
        # Aplicar actualizaciones
        updated_count = 0
        for update in objects_updates:
            object_id = str(update.get('object_id'))
            
            if object_id not in objects_dict:
                print(f"⚠️ Objeto {object_id} no encontrado en el modelo 3D")
                continue
            
            obj = objects_dict[object_id]
            
            # Actualizar dimensiones
            if 'width' in update and update['width'] is not None:
                if 'dimensions' not in obj:
                    obj['dimensions'] = {}
                obj['dimensions']['width'] = update['width']
            
            if 'height' in update and update['height'] is not None:
                if 'dimensions' not in obj:
                    obj['dimensions'] = {}
                obj['dimensions']['height'] = update['height']
            
            if 'depth' in update and update['depth'] is not None:
                if 'dimensions' not in obj:
                    obj['dimensions'] = {}
                obj['dimensions']['depth'] = update['depth']
            
            # Actualizar posición
            if 'position' in update and update['position'] is not None:
                if 'position' not in obj:
                    obj['position'] = {}
                
                pos = update['position']
                if 'x' in pos and pos['x'] is not None:
                    obj['position']['x'] = pos['x']
                if 'y' in pos and pos['y'] is not None:
                    obj['position']['y'] = pos['y']
                if 'z' in pos and pos['z'] is not None:
                    obj['position']['z'] = pos['z']
            
            updated_count += 1
        
        # Actualizar datos_json con los objetos modificados
        datos_json['objects'] = list(objects_dict.values())
        
        # Guardar en la base de datos
        modelo3d_updated = self.modelo3d_repo.update(plano_id, datos_json, "generado")
        
        if not modelo3d_updated:
            return {
                "success": False,
                "error": "Error al guardar las actualizaciones en la base de datos"
            }
        
        return {
            "success": True,
            "message": f"{updated_count} objeto(s) actualizado(s) exitosamente",
            "updated_count": updated_count,
            "datos_json": datos_json
        }
    
    def _extract_measurements(self, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extraer medidas relevantes del plano para cotización
        
        Args:
            verification_data: Datos del modelo 3D del API de conversión
            
        Returns:
            Dict con medidas extraídas (área, perímetro, conteos, etc.)
        """
        try:
            objects = verification_data.get('objects', [])
            scene = verification_data.get('scene', {})
            bounds = scene.get('bounds', {})
            
            # Contadores de elementos
            num_paredes = 0
            num_ventanas = 0
            num_puertas = 0
            
            # Medidas acumuladas
            area_paredes = 0.0
            area_ventanas = 0.0
            area_puertas = 0.0
            perimetro_total = 0.0
            
            # Detalles de objetos
            objetos_detalle = []
            
            for obj in objects:
                obj_type = obj.get('type', '')
                dimensions = obj.get('dimensions', {})
                position = obj.get('position', {})
                
                width = dimensions.get('width', 0)
                height = dimensions.get('height', 0)
                depth = dimensions.get('depth', 0)
                
                # Calcular área del objeto (aproximación)
                area = width * height if width and height else 0
                
                obj_detail = {
                    'id': obj.get('id'),
                    'tipo': obj_type,
                    'ancho': round(width, 2),
                    'alto': round(height, 2),
                    'profundidad': round(depth, 2),
                    'area': round(area, 2),
                    'posicion': {
                        'x': round(position.get('x', 0), 2),
                        'y': round(position.get('y', 0), 2),
                        'z': round(position.get('z', 0), 2)
                    }
                }
                
                # Contar elementos y acumular áreas
                if obj_type == 'wall':
                    num_paredes += 1
                    area_paredes += area
                    perimetro_total += width  # Aproximación del perímetro
                elif obj_type == 'window':
                    num_ventanas += 1
                    area_ventanas += area
                elif obj_type == 'door':
                    num_puertas += 1
                    area_puertas += area
                
                objetos_detalle.append(obj_detail)
            
            # Calcular área total del plano (desde bounds)
            area_total = bounds.get('width', 0) * bounds.get('height', 0)
            
            medidas = {
                'area_total': round(area_total, 2),
                'area_paredes': round(area_paredes, 2),
                'area_ventanas': round(area_ventanas, 2),
                'area_puertas': round(area_puertas, 2),
                'perimetro_total': round(perimetro_total, 2),
                'num_paredes': num_paredes,
                'num_ventanas': num_ventanas,
                'num_puertas': num_puertas,
                'bounds': {
                    'ancho': round(bounds.get('width', 0), 2),
                    'alto': round(bounds.get('height', 0), 2)
                },
                'objetos': objetos_detalle,
                'total_objetos': len(objects)
            }
            
            return medidas
            
        except Exception as e:
            print(f"⚠️ Error extrayendo medidas: {e}")
            # Retornar medidas vacías en caso de error
            return {
                'area_total': 0,
                'perimetro_total': 0,
                'num_paredes': 0,
                'num_ventanas': 0,
                'num_puertas': 0,
                'objetos': [],
                'error': str(e)
            }