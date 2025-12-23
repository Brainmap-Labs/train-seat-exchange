from datetime import datetime
from typing import List, Optional, Literal
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

BerthType = Literal["LB", "MB", "UB", "SL", "SU"]
ClassType = Literal["SL", "3A", "2A", "1A", "CC", "EC", "2S"]
BookingStatus = Literal["CNF", "RAC", "WL", "RLWL", "PQWL"]
TicketStatus = Literal["active", "completed", "cancelled"]

class Station(BaseModel):
    code: str
    name: str

class Passenger(BaseModel):
    id: str = Field(default_factory=lambda: str(PydanticObjectId()))
    name: str
    age: int
    gender: Literal["M", "F", "O"]
    coach: str
    seat_number: int
    berth_type: BerthType
    booking_status: BookingStatus
    current_status: BookingStatus

class Ticket(Document):
    user_id: PydanticObjectId
    pnr: str
    train_number: str
    train_name: str
    travel_date: datetime
    boarding_station: Station
    destination_station: Station
    class_type: ClassType
    quota: str = "GN"
    passengers: List[Passenger]
    status: TicketStatus = "active"
    raw_image_url: Optional[str] = None
    ocr_confidence: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "tickets"
        indexes = [
            "user_id",
            "pnr",
            "train_number",
            "travel_date",
        ]

    # Optional matching preferences stored on ticket
    preferred_berth: Optional[List[BerthType]] = None
    allow_cyclic: bool = False
    same_coach_only: bool = False
    same_bay_only: bool = False
    min_match_score: float = 60.0

    def is_scattered(self) -> bool:
        """Check if passengers are in different coaches"""
        coaches = set(p.coach for p in self.passengers)
        return len(coaches) > 1

    def get_coaches(self) -> List[str]:
        """Get unique coaches for this ticket"""
        return list(set(p.coach for p in self.passengers))

