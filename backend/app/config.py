from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PRAHARI Crime Intelligence"
    database_url: str = "sqlite:///./data/prahari.db"
    mistral_api_key: str = ""
    sarvam_api_key: str = ""
    llm_provider: str = "mock"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "prahari-demo"
    jwt_secret: str = "dev-only-secret"
    audit_signing_key: str = "dev-only-audit-key"
    cors_origins: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

