#!/usr/bin/env python3
"""
Script de ejemplo para probar la API FloorPlanTo3D con Swagger
Este script demuestra cómo usar los endpoints principales de la API
"""

import requests
import json
from typing import Dict, Any

# Configuración base
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"  # Ajusta según tu configuración

class APIClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def set_token(self, token: str):
        """Configurar token JWT para autenticación"""
        self.token = token
        self.session.headers.update({
            "Authorization": f"Bearer {token}"
        })
    
    def register_user(self, correo: str, contrasena: str, nombre: str) -> Dict[str, Any]:
        """Registrar nuevo usuario"""
        data = {
            "correo": correo,
            "contrasena": contrasena,
            "nombre": nombre
        }
        response = self.session.post(f"{self.base_url}/auth/register", json=data)
        return response.json()
    
    def login(self, correo: str, contrasena: str) -> Dict[str, Any]:
        """Iniciar sesión"""
        data = {
            "correo": correo,
            "contrasena": contrasena
        }
        response = self.session.post(f"{self.base_url}/auth/login", json=data)
        return response.json()
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Obtener dashboard del usuario"""
        response = self.session.get(f"{self.base_url}/dashboard/")
        return response.json()
    
    def get_membresias(self) -> Dict[str, Any]:
        """Obtener lista de membresías"""
        response = self.session.get(f"{self.base_url}/membresias/")
        return response.json()
    
    def create_membresia(self, nombre: str, precio: float, duracion: int, descripcion: str = None) -> Dict[str, Any]:
        """Crear nueva membresía"""
        data = {
            "nombre": nombre,
            "precio": precio,
            "duracion": duracion,
            "descripcion": descripcion
        }
        response = self.session.post(f"{self.base_url}/membresias/", json=data)
        return response.json()
    
    def get_users(self) -> Dict[str, Any]:
        """Obtener lista de usuarios"""
        response = self.session.get(f"{self.base_url}/users/")
        return response.json()

def main():
    """Función principal para demostrar el uso de la API"""
    print("🚀 Iniciando prueba de la API FloorPlanTo3D")
    print("=" * 50)
    
    # Crear cliente API
    client = APIClient()
    
    # Datos de prueba
    test_user = {
        "correo": "test@ejemplo.com",
        "contrasena": "password123",
        "nombre": "Usuario de Prueba"
    }
    
    try:
        # 1. Registrar usuario
        print("📝 1. Registrando usuario...")
        register_response = client.register_user(**test_user)
        print(f"✅ Usuario registrado: {register_response.get('message')}")
        
        # Configurar token automáticamente
        if 'access_token' in register_response:
            client.set_token(register_response['access_token'])
            print("🔑 Token JWT configurado automáticamente")
        
        # 2. Obtener dashboard
        print("\n🏠 2. Obteniendo dashboard...")
        dashboard = client.get_dashboard()
        print(f"✅ Dashboard obtenido para: {dashboard['usuario']['nombre']}")
        
        # 3. Obtener membresías
        print("\n💳 3. Obteniendo membresías...")
        membresias = client.get_membresias()
        print(f"✅ Encontradas {len(membresias)} membresías")
        
        # 4. Crear nueva membresía
        print("\n➕ 4. Creando nueva membresía...")
        nueva_membresia = client.create_membresia(
            nombre="Plan de Prueba",
            precio=19.99,
            duracion=15,
            descripcion="Plan de prueba creado desde script"
        )
        print(f"✅ Membresía creada: {nueva_membresia['nombre']}")
        
        # 5. Obtener usuarios
        print("\n👥 5. Obteniendo lista de usuarios...")
        usuarios = client.get_users()
        print(f"✅ Encontrados {len(usuarios)} usuarios")
        
        print("\n🎉 ¡Todas las pruebas completadas exitosamente!")
        print("\n📋 Resumen de la sesión:")
        print(f"   - Usuario registrado: {test_user['nombre']}")
        print(f"   - Token JWT: {'✅ Configurado' if client.token else '❌ No configurado'}")
        print(f"   - Membresías disponibles: {len(membresias)}")
        print(f"   - Usuarios en sistema: {len(usuarios)}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor FastAPI esté ejecutándose en http://localhost:8000")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP: {e}")
        print("   Revisa los logs del servidor para más detalles")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_swagger_endpoints():
    """Función para probar endpoints específicos de Swagger"""
    print("\n🔍 Probando endpoints específicos de Swagger...")
    
    client = APIClient()
    
    # Probar endpoint sin autenticación
    try:
        print("📡 Probando endpoint público...")
        response = requests.get(f"{BASE_URL}/membresias/")
        if response.status_code == 200:
            print("✅ Endpoint público funciona correctamente")
        else:
            print(f"⚠️ Endpoint público devolvió código: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en endpoint público: {e}")
    
    # Probar endpoint protegido sin token
    try:
        print("🔒 Probando endpoint protegido sin token...")
        response = requests.get(f"{BASE_URL}/dashboard/")
        if response.status_code == 401:
            print("✅ Endpoint protegido correctamente rechaza requests sin token")
        else:
            print(f"⚠️ Endpoint protegido devolvió código inesperado: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en endpoint protegido: {e}")

if __name__ == "__main__":
    print("🎯 Script de prueba para API FloorPlanTo3D")
    print("Este script demuestra cómo usar los endpoints principales")
    print("Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    print()
    
    # Ejecutar pruebas principales
    main()
    
    # Ejecutar pruebas específicas de Swagger
    test_swagger_endpoints()
    
    print("\n📚 Para más información, consulta SWAGGER_GUIDE.md")
    print("🌐 Accede a Swagger UI en: http://localhost:8000/docs")
