from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    TOKEN_SECONDS_EXP: int
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()
