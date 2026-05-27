from datetime import datetime
from typing import Literal, Optional
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING

AuthProvider = Literal["phone", "google"]

class User(Document):
    phone: Optional[str] = None
    google_id: Optional[str] = None
    auth_provider: AuthProvider = "phone"
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
        indexes = [
            IndexModel([("phone", ASCENDING)], unique=True, sparse=True),
            IndexModel([("google_id", ASCENDING)], unique=True, sparse=True),
            # Partial unique: many phone-OTP users have no email (null)
            IndexModel(
                [("email", ASCENDING)],
                unique=True,
                name="email_unique_nonempty",
                partialFilterExpression={"email": {"$type": "string"}},
            ),
        ]
        
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

