"""
Configuración de seguridad para Swagger UI
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi(app: FastAPI):
    """
    Personaliza la documentación OpenAPI para incluir configuración de seguridad JWT
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Agregar configuración de seguridad JWT
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Ingresa tu token JWT obtenido del endpoint de login"
        }
    }
    
    # Agregar seguridad global
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # Personalizar información adicional
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    # Agregar tags personalizados
    openapi_schema["tags"] = [
        {
            "name": "Autenticación",
            "description": "Endpoints para registro, login y gestión de usuarios"
        },
        {
            "name": "Membresías",
            "description": "Gestión de planes de membresía y suscripciones"
        },
        {
            "name": "Dashboard",
            "description": "Panel de control del usuario autenticado"
        },
        {
            "name": "Pagos",
            "description": "Gestión de pagos e integración con Stripe"
        },
        {
            "name": "Suscripciones",
            "description": "Control de suscripciones de usuarios"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
