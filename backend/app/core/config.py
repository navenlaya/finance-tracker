from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Plaid credentials
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    PLAID_ENV: str = "sandbox"
    FERNET_KEY: str

    class Config:
        env_file = ".env"

# Only instantiate settings when environment variables are available (e.g., at runtime, not at import time for Alembic)
settings = Settings()
