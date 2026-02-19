from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):

    DATABASE_URL: str

    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5174"]

    SECRET_KEY: str
    ALGORITHM: str
    
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()