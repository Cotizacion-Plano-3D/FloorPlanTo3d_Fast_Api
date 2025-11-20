from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    TOKEN_SECONDS_EXP: int = 3600  # 1 hora por defecto
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    FRONTEND_URL: str = "https://floorplanto3dfrontendreact-eight.vercel.app"  # URL del frontend
    FLOORPLAN_API_URL: str = "https://floorplanto3dapi-production.up.railway.app"  # URL del servicio Flask
    GOOGLE_DRIVE_FOLDER_ID: str = "1_Mv_vpgc-0LCEuPaI49Ym3xvzvRhW7OW"  # ID del folder de Google Drive
    GOOGLE_CREDENTIALS_PATH: str = "./credentials.json"
    GOOGLE_OAUTH_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"
    class Config:
        env_file = ".env"

settings = Settings()
