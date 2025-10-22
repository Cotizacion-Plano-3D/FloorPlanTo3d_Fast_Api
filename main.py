from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.security import HTTPBearer
from routers.register import router as register_router
from routers.login import router as login_router
from routers.dashboard import router as dashboard_router
from routers.users import router as users_router
from routers.stripe import router as stripe_router
from routers.stripe_create_membresia import router as stripe_create_membresia_router
from routers.stripe_webhook import router as stripe_webhook_router
from routers.membresia import router as membresia_router
from routers.suscripcion import router as suscripcion_router
from routers.pago import router as pago_router
from swagger_config import custom_openapi
import logging
# main.py de FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Consola
        logging.FileHandler('stripe_debug.log')  # Archivo
    ]
)

# Configuración detallada de FastAPI para Swagger
app = FastAPI(
    title="FloorPlanTo3D API",
    version="1.0.0",
    contact={
        "name": "Equipo FloorPlanTo3D",
        "email": "support@floorplant3d.com",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",  # URL para Swagger UI
    redoc_url="/redoc",  # URL para ReDoc
    openapi_url="/openapi.json",  # URL para el esquema OpenAPI
)

bearer_scheme = HTTPBearer()

# Incluir routers
app.include_router(register_router)
app.include_router(login_router)
app.include_router(dashboard_router)
app.include_router(
    users_router
)

app.include_router(membresia_router)
app.include_router(suscripcion_router)
app.include_router(pago_router)
app.include_router(stripe_router)
app.include_router(stripe_create_membresia_router)
app.include_router(stripe_webhook_router)

origins = [
    "http://localhost:5173",  # URL de tu frontend React
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # URL de tu frontend React
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # permite estas URLs
    allow_credentials=True,
    allow_methods=["*"],     # permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],     # permite headers personalizados
)

# Configurar OpenAPI personalizado
app.openapi = lambda: custom_openapi(app)