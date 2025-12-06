from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Train Seat Exchange"
    DEBUG: bool = True
    
    # Database
    MONGODB_URL: str = "mongodb+srv://sanjayazad_db_user:XzDU2eFYxxRN0dwY@cluster0.hh5j5vb.mongodb.net/?appName=Cluster0"
    DATABASE_NAME: str = "train_seat_exchange"
    
    # Auth
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # OCR (fallback option)
    # Hugging Face OCR Model (recommended for better accuracy)
    HUGGINGFACE_MODEL: str = "nanonets/Nanonets-OCR2-3B"  # or "microsoft/trocr-base-printed"
    USE_HUGGINGFACE_OCR: bool = False  # Set to False to use Tesseract instead
    TESSERACT_CMD: Optional[str] = None  # Optional path to tesseract executable
    
    # PNR Lookup API
    INDIAN_RAIL_API_KEY: Optional[str] = None  # API key for Indian Rail API
    INDIAN_RAIL_API_URL: str = "https://indianrailapi.com/api/v2"  # Base URL for PNR API
    
    class Config:
        env_file = ".env"

settings = Settings()

