from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Optional
from functools import lru_cache

# backend/.env — resolved from this file (app/core/config.py), not from cwd
_BACKEND_DIR = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_DIR / ".env"

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Train Seat Exchange"
    DEBUG: bool = True
    
    # Database
    MONGODB_URL: str = ""  # Read from .env - required for database connection
    
    DATABASE_NAME: str = "train_seat_exchange"
    
    # Auth
    SECRET_KEY: str = "your-secret-key-change-in-production"  # Should be set in .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"

    # Google OAuth (same client ID as frontend VITE_GOOGLE_CLIENT_ID)
    GOOGLE_CLIENT_ID: Optional[str] = None
    
    # CORS - can be comma-separated string in .env or list
    CORS_ORIGINS: str = "http://localhost:3001,https://train-seat-exchange.vercel.app/"
    
    # OCR (fallback option)
    # Hugging Face OCR Model (recommended for better accuracy)
    HUGGINGFACE_MODEL: str = "nanonets/Nanonets-OCR2-3B"  # or "microsoft/trocr-base-printed"
    USE_HUGGINGFACE_OCR: bool = False  # Set to False to use Tesseract instead
    TESSERACT_CMD: Optional[str] = None  # Optional path to tesseract executable
    
    # AI — Ticket parsing & matching (OpenAI and/or Google Gemini)
    AI_PROVIDER: str = "auto"  # auto | openai | gemini
    USE_OPENAI_PARSING: bool = True  # Enables AI ticket parsing (any configured provider)
    USE_OPENAI_MATCHING: bool = True  # Enables AI match re-ranking (any configured provider)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"
    AI_MATCHING_TOP_N: int = 5  # Number of matches to send to AI for re-ranking
    # Admin API key for protected admin endpoints (set in .env)
    ADMIN_API_KEY: Optional[str] = None
    
    # PNR Lookup API
    INDIAN_RAIL_API_KEY: Optional[str] = None  # API key for Indian Rail API
    INDIAN_RAIL_API_URL: str = "https://indianrailapi.com/api/v2"  # Base URL for PNR API
    
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.is_file() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env
    )

    @field_validator("MONGODB_URL", mode="before")
    @classmethod
    def normalize_mongodb_url(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        url = value.strip()
        # Docker --env-file and some .env editors leave surrounding quotes in the value
        if len(url) >= 2 and url[0] == url[-1] and url[0] in ("'", '"'):
            url = url[1:-1].strip()
        return url

    @property
    def ai_parsing_enabled(self) -> bool:
        return self.USE_OPENAI_PARSING and bool(self.OPENAI_API_KEY or self.GEMINI_API_KEY)

    @property
    def ai_matching_enabled(self) -> bool:
        return self.USE_OPENAI_MATCHING and bool(self.OPENAI_API_KEY or self.GEMINI_API_KEY)

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()

settings = get_settings()

