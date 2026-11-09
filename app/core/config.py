from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Půjčovna vybavení – Hory a voda"
    API_V1_STR: str = "/api/v1"
    
    # Databáze: výchozí SQLite pro lokální spuštění bez daemona, v dockeru PostgreSQL
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Bezpečnost a JWT
    SECRET_KEY: str = "ppro-secret-key-change-in-production-only-synthetic-test"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hodin (směna obsluhy)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
