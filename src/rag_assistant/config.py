from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./rag.db"
    qdrant_path: str = "./qdrant_data"
    upload_dir: str = "./uploads"
    evidence_threshold: float = Field(default=0.18, ge=0, le=1)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
