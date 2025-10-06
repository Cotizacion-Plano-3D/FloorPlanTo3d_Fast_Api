"""
Configuración adicional para mejorar la experiencia de Swagger UI
"""

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

def add_swagger_customizations(app: FastAPI):
    """
    Agrega personalizaciones adicionales a Swagger UI
    """
    
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        """
        Swagger UI personalizado con configuración mejorada
        """
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Documentación Interactiva",
            oauth2_redirect_url="/docs/oauth2-redirect",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
            swagger_ui_parameters={
                "deepLinking": True,
                "displayOperationId": False,
                "defaultModelsExpandDepth": 2,
                "defaultModelExpandDepth": 2,
                "defaultModelRendering": "example",
                "displayRequestDuration": True,
                "docExpansion": "list",
                "filter": True,
                "showExtensions": True,
                "showCommonExtensions": True,
                "tryItOutEnabled": True,
                "requestSnippetsEnabled": True,
                "syntaxHighlight": {
                    "activate": True,
                    "theme": "agate"
                }
            }
        )

def add_examples_to_openapi(app: FastAPI):
    """
    Agrega ejemplos adicionales a la documentación OpenAPI
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Agregar ejemplos globales
    openapi_schema["info"]["x-examples"] = {
        "login_example": {
            "summary": "Ejemplo de Login",
            "description": "Ejemplo completo de cómo hacer login",
            "value": {
                "correo": "usuario@ejemplo.com",
                "contrasena": "miPassword123"
            }
        },
        "register_example": {
            "summary": "Ejemplo de Registro",
            "description": "Ejemplo completo de cómo registrar un usuario",
            "value": {
                "correo": "nuevo@ejemplo.com",
                "contrasena": "miPassword123",
                "nombre": "Juan Pérez"
            }
        },
        "membresia_example": {
            "summary": "Ejemplo de Membresía",
            "description": "Ejemplo de cómo crear una membresía",
            "value": {
                "nombre": "Plan Premium",
                "precio": 49.99,
                "duracion": 30,
                "descripcion": "Plan premium con todas las funciones avanzadas"
            }
        }
    }
    
    # Agregar información de contacto extendida
    openapi_schema["info"]["contact"]["x-github"] = "https://github.com/tu-usuario/floorplant3d-api"
    openapi_schema["info"]["contact"]["x-support"] = "support@floorplant3d.com"
    
    # Agregar información de licencia extendida
    openapi_schema["info"]["license"]["url"] = "https://opensource.org/licenses/MIT"
    
    # Agregar información del servidor
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Servidor de desarrollo local"
        },
        {
            "url": "https://api.floorplant3d.com",
            "description": "Servidor de producción"
        }
    ]
    
    # Agregar información de seguridad extendida
    openapi_schema["components"]["securitySchemes"]["BearerAuth"]["x-bearerInfoFunc"] = "swaggerGlobalAuth"
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
