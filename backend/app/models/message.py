from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field

class Message(Document):
    exchange_id: PydanticObjectId
    sender_id: PydanticObjectId
    content: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "messages"
        indexes = [
            "exchange_id",
            "sender_id",
            "created_at",
        ]

