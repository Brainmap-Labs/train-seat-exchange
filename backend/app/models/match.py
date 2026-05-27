from datetime import datetime
from typing import List, Dict, Any, Optional
from beanie import Document
from pydantic import Field

class MatchSuggestion(Document):
    ticket_id: str
    train_number: str
    travel_date: datetime
    suggestions: List[Dict[str, Any]] = []
    source: str = "auto"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "match_suggestions"
        indexes = [
            "ticket_id",
            "train_number",
            "travel_date",
        ]
