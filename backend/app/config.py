from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/freestyle_callificator"
    SQLALCHEMY_ECHO: bool = False

    # API Settings
    DEBUG: bool = True
    API_TITLE: str = "Freestyle Callificator API"
    API_VERSION: str = "0.1.0"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    TEMP_DIR: str = "./temp"

    # Processing
    MAX_FILE_SIZE: int = 1000000000  # 1GB

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
