"""
Core configuration settings for the Finance Tracker application.
Manages environment variables and application settings.
"""

from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = "Finance Tracker"
    app_version: str = "1.0.0"
    debug: bool = True
    api_prefix: str = "/api/v1"
    
    # Database settings
    database_url: Optional[str] = None
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "finance_tracker"
    db_user: str = "postgres"
    db_password: str = "password"
    
    @validator("database_url", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        """Build database URL if not provided."""
        if isinstance(v, str):
            return v
        return f"postgresql+asyncpg://{values.get('db_user')}:{values.get('db_password')}@{values.get('db_host')}:{values.get('db_port')}/{values.get('db_name')}"
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    backend_cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]
    
    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from environment variable."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Plaid API settings
    plaid_client_id: Optional[str] = None
    plaid_secret: Optional[str] = None
    plaid_env: str = "sandbox"  # sandbox, development, or production
    plaid_products: List[str] = ["transactions", "auth", "identity"]
    plaid_country_codes: List[str] = ["US"]
    
    # Redis settings for Celery
    redis_url: str = "redis://localhost:6379/0"
    
    # ML settings
    ml_model_path: str = "models/"
    retrain_interval_days: int = 7
    forecast_days: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 