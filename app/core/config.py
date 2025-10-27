from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union


class Settings(BaseSettings):
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI Studio Backend"
    VERSION: str = "1.0.0"
    
    # Database (default to SQLite)
    DATABASE_URL: str = "sqlite:///./ai_studio.db"
    
    # Security (default for development)
    SECRET_KEY: str = "development-secret-key-change-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # JWT Settings
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production-67890"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # First Admin User (created on startup if doesn't exist)
    FIRST_ADMIN_EMAIL: str = ""
    
    # CORS - store as string in .env, parsed to list
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000"
    
    # Ngrok
    NGROK_AUTH_TOKEN: str = ""
    NGROK_DOMAIN: str = ""
    NGROK_PUBLIC_URL: str = ""  # Full public URL (e.g., https://domain.ngrok-free.dev/AIStudio)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding='utf-8',
        extra='ignore'  # Ignore extra fields
    )
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Handle comma-separated string
            if ',' in v:
                return [origin.strip() for origin in v.split(',') if origin.strip()]
            # Handle single origin
            return [v.strip()] if v.strip() else ["http://localhost:3000"]
        return ["http://localhost:3000"]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return self.parse_cors_origins(self.CORS_ORIGINS)


# Load settings with fallback
try:
    settings = Settings()
    print("✅ Settings loaded from .env file")
except Exception as e:
    print(f"⚠️  Warning: Could not load settings from .env: {e}")
    print("Using default settings for development")
    # Create minimal settings without loading .env
    import os
    os.environ.pop('CORS_ORIGINS', None)  # Remove problematic env var
    settings = Settings(
        DATABASE_URL="sqlite:///./ai_studio.db",
        SECRET_KEY="development-secret-key-change-in-production-12345",
        CORS_ORIGINS=["http://localhost:3000"]
    )
