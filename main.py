from fastapi import FastAPI
from auth.register import router as register_router
from auth.login import router as login_router
from auth.dashboard import router as dashboard_router
from auth.logout import router as logout_router  # Importamos logout
from auth.users import router as users_router  # Importamos users
from auth.stripe import router as stripe_router
from auth.stripe_create_membresia import router as stripe_create_membresia_router
from auth.stripe_webhook import router as stripe_webhook_router
from routers.membresia import router as membresia_router
from routers.suscripcion import router as suscripcion_router
from routers.pago import router as pago_router

# main.py de FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Incluir routers de auth
app.include_router(register_router)
app.include_router(login_router)
app.include_router(dashboard_router)
app.include_router(logout_router)  # Incluir logout
app.include_router(users_router)   # Incluir users
app.include_router(membresia_router)
app.include_router(suscripcion_router)
app.include_router(pago_router)
app.include_router(stripe_router)
app.include_router(stripe_create_membresia_router)
app.include_router(stripe_webhook_router)

origins = [
    "http://localhost:5173",  # URL de tu frontend React
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # permite estas URLs
    allow_credentials=True,
    allow_methods=["*"],     # permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],     # permite headers personalizados
)