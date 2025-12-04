from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field

class User(Document):
    phone: str = Field(..., unique=True)
    name: str = ""
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    rating: float = 0.0
    total_ratings: int = 0
    total_exchanges: int = 0
    is_verified: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        
    class Config:
        json_schema_extra = {
            "example": {
                "phone": "9876543210",
                "name": "Rahul Kumar",
                "email": "rahul@example.com",
                "rating": 4.5,
                "total_exchanges": 5,
            }
        }

    def update_rating(self, new_rating: float):
        """Update user rating with new review"""
        total = self.rating * self.total_ratings + new_rating
        self.total_ratings += 1
        self.rating = total / self.total_ratings

