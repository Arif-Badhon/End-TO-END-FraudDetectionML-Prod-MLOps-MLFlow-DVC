from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings - ALL values loaded from .env
    No defaults in code - everything must be in .env
    This ensures consistent configuration across environments
    """
    
    # ============================================
    # Database Configuration
    # ============================================
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_URL: str
    
    # ============================================
    # PgAdmin Configuration
    # ============================================
    PGADMIN_EMAIL: str
    PGADMIN_PASSWORD: str
    PGADMIN_PORT: int
    
    # ============================================
    # Application Configuration
    # ============================================
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool
    ENVIRONMENT: str
    
    # ============================================
    # API Configuration
    # ============================================
    API_HOST: str
    API_PORT: int
    API_WORKERS: int
    
    # ============================================
    # MLflow Configuration
    # ============================================
    MLFLOW_TRACKING_URI: str
    MLFLOW_EXPERIMENT_NAME: str
    
    # ============================================
    # Paths
    # ============================================
    MODEL_PATH: str
    DATA_PATH: str
    FEAST_REPO_PATH: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Create a cached instance of settings
    Returns same instance on subsequent calls (performance optimization)
    """
    return Settings()


# For easy access
settings = get_settings()
