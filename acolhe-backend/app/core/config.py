from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    APP_NAME: str = "Acolhe.app"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
