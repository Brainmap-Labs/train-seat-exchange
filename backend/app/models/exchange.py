from datetime import datetime
from typing import List, Optional, Literal
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

ExchangeStatus = Literal["pending", "accepted", "declined", "completed", "expired"]

class SeatInfo(BaseModel):
    passenger_id: str
    passenger_name: str
    coach: str
    seat_number: int
    berth_type: str

class ExchangeProposal(BaseModel):
    give: List[SeatInfo]
    receive: List[SeatInfo]
    improvement_score: float = 0.0

class ExchangeRequest(Document):
    requester_id: PydanticObjectId
    requester_ticket_id: PydanticObjectId
    target_user_id: PydanticObjectId
    target_ticket_id: PydanticObjectId
    train_number: str
    travel_date: datetime
    proposal: ExchangeProposal
    status: ExchangeStatus = "pending"
    message: Optional[str] = None
    requester_confirmed: bool = False
    target_confirmed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    class Settings:
        name = "exchange_requests"
        indexes = [
            "requester_id",
            "target_user_id",
            "train_number",
            "travel_date",
            "status",
        ]

    def can_complete(self) -> bool:
        """Check if both parties have confirmed"""
        return self.requester_confirmed and self.target_confirmed

