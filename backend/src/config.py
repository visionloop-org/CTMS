"""
CTMS Backend Configuration Module
Loads settings from environment variables with safe defaults.
"""
import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Settings:
    # Environment
    ENV: str = os.getenv("CTMS_ENV", "development")
    DEBUG: bool = os.getenv("CTMS_DEBUG", "true").lower() in ("true", "1", "yes")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://ctms_dev:ctms_password@localhost:5432/ctms_db"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://:redis_local_pass@localhost:6379/0")
    
    # Zoho Integration
    ZOHO_CLIENT_ID: str = os.getenv("ZOHO_CLIENT_ID", "mock_client_id")
    ZOHO_CLIENT_SECRET: str = os.getenv("ZOHO_CLIENT_SECRET", "mock_client_secret")
    ZOHO_REFRESH_TOKEN: str = os.getenv("ZOHO_REFRESH_TOKEN", "mock_refresh_token")
    ZOHO_BASE_URL: str = os.getenv("ZOHO_BASE_URL", "http://localhost:8089")
    ZOHO_BOOKS_ORG_ID: str = os.getenv("ZOHO_BOOKS_ORG_ID", "mock_org_88192")
    
    # Security & API Key
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-ctms-master-jwt-key")
    DEFAULT_API_KEY_RPM: int = int(os.getenv("DEFAULT_API_KEY_RPM", "300"))
    
    # Safety Limits
    MAX_TARE_LOSS_PERCENT: float = 5.0
    HYDRO_TEST_WARNING_DAYS: int = 30


settings = Settings()
