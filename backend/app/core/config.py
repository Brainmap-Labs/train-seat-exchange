from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Optional
from functools import lru_cache

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
    
    # CORS - can be comma-separated string in .env or list
    CORS_ORIGINS: str = "http://localhost:3000,https://train-seat-exchange.vercel.app/"
    
    # OCR (fallback option)
    # Hugging Face OCR Model (recommended for better accuracy)
    HUGGINGFACE_MODEL: str = "nanonets/Nanonets-OCR2-3B"  # or "microsoft/trocr-base-printed"
    USE_HUGGINGFACE_OCR: bool = False  # Set to False to use Tesseract instead
    TESSERACT_CMD: Optional[str] = None  # Optional path to tesseract executable
    
    # Ticket Text Parsing Method
    USE_OPENAI_PARSING: bool = True  # Set to True to use OpenAI for parsing, False for regex
    OPENAI_API_KEY: Optional[str] = None  # Should be set in .env
    OPENAI_MODEL: str = "gpt-4o-mini"  # OpenAI model to use for parsing
    
    # AI-Enhanced Matching Algorithm
    USE_OPENAI_MATCHING: bool = True  # Enable AI-powered seat matching optimization
    AI_MATCHING_TOP_N: int = 5  # Number of matches to send to AI for re-ranking
    
    # PNR Lookup API
    INDIAN_RAIL_API_KEY: Optional[str] = None  # API key for Indian Rail API
    INDIAN_RAIL_API_URL: str = "https://indianrailapi.com/api/v2"  # Base URL for PNR API
    
    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()

settings = get_settings()

