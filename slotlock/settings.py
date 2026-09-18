from functools import lru_cache

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    database_url: PostgresDsn

    @field_validator('database_url')
    @classmethod
    def require_asyncpg(cls, value: PostgresDsn) -> PostgresDsn:
        if value.scheme != 'postgresql+asyncpg':
            raise ValueError('DATABASE_URL must use postgresql+asyncpg')
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
