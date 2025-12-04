from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId

from app.core.security import get_current_user
from app.models.user import User
from app.models.ticket import Ticket, Passenger, Station
from app.services.ocr_service import OCRService

router = APIRouter()

class PassengerCreate(BaseModel):
    name: str
    age: int
    gender: str
    coach: str
    seat_number: int
    berth_type: str
    booking_status: str = "CNF"
    current_status: str = "CNF"

class TicketCreate(BaseModel):
    pnr: str
    train_number: str
    train_name: str
    travel_date: datetime
    boarding_station_code: str
    boarding_station_name: str
    destination_station_code: str
    destination_station_name: str
    class_type: str
    quota: str = "GN"
    passengers: List[PassengerCreate]

class TicketResponse(BaseModel):
    id: str
    pnr: str
    train_number: str
    train_name: str
    travel_date: datetime
    boarding_station: dict
    destination_station: dict
    class_type: str
    passengers: List[dict]
    status: str
    is_scattered: bool

@router.post("/upload")
async def upload_ticket_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload ticket image for OCR processing"""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: JPEG, PNG, PDF"
        )
    
    # Read file content
    content = await file.read()
    
    # Process with OCR
    ocr_service = OCRService()
    extracted_data = await ocr_service.extract_ticket_data(content, file.content_type)
    
    return {
        "message": "Ticket processed successfully",
        "data": extracted_data,
        "confidence": extracted_data.get("confidence", 0)
    }

@router.post("", response_model=TicketResponse)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new ticket"""
    # Check for duplicate PNR
    existing = await Ticket.find_one(
        Ticket.pnr == ticket_data.pnr,
        Ticket.user_id == current_user.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket with this PNR already exists"
        )
    
    # Create passengers
    passengers = [
        Passenger(
            name=p.name,
            age=p.age,
            gender=p.gender,
            coach=p.coach,
            seat_number=p.seat_number,
            berth_type=p.berth_type,
            booking_status=p.booking_status,
            current_status=p.current_status,
        )
        for p in ticket_data.passengers
    ]
    
    # Create ticket
    ticket = Ticket(
        user_id=current_user.id,
        pnr=ticket_data.pnr,
        train_number=ticket_data.train_number,
        train_name=ticket_data.train_name,
        travel_date=ticket_data.travel_date,
        boarding_station=Station(
            code=ticket_data.boarding_station_code,
            name=ticket_data.boarding_station_name
        ),
        destination_station=Station(
            code=ticket_data.destination_station_code,
            name=ticket_data.destination_station_name
        ),
        class_type=ticket_data.class_type,
        quota=ticket_data.quota,
        passengers=passengers,
    )
    
    await ticket.insert()
    
    return TicketResponse(
        id=str(ticket.id),
        pnr=ticket.pnr,
        train_number=ticket.train_number,
        train_name=ticket.train_name,
        travel_date=ticket.travel_date,
        boarding_station=ticket.boarding_station.model_dump(),
        destination_station=ticket.destination_station.model_dump(),
        class_type=ticket.class_type,
        passengers=[p.model_dump() for p in ticket.passengers],
        status=ticket.status,
        is_scattered=ticket.is_scattered(),
    )

@router.get("")
async def get_tickets(current_user: User = Depends(get_current_user)):
    """Get all tickets for current user"""
    tickets = await Ticket.find(Ticket.user_id == current_user.id).to_list()
    
    return [
        {
            "id": str(t.id),
            "pnr": t.pnr,
            "train_number": t.train_number,
            "train_name": t.train_name,
            "travel_date": t.travel_date,
            "boarding_station": t.boarding_station.model_dump(),
            "destination_station": t.destination_station.model_dump(),
            "class_type": t.class_type,
            "passengers": [p.model_dump() for p in t.passengers],
            "status": t.status,
            "is_scattered": t.is_scattered(),
        }
        for t in tickets
    ]

@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get ticket by ID"""
    ticket = await Ticket.get(PydanticObjectId(ticket_id))
    
    if not ticket or ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    return {
        "id": str(ticket.id),
        "pnr": ticket.pnr,
        "train_number": ticket.train_number,
        "train_name": ticket.train_name,
        "travel_date": ticket.travel_date,
        "boarding_station": ticket.boarding_station.model_dump(),
        "destination_station": ticket.destination_station.model_dump(),
        "class_type": ticket.class_type,
        "passengers": [p.model_dump() for p in ticket.passengers],
        "status": ticket.status,
        "is_scattered": ticket.is_scattered(),
    }

@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a ticket"""
    ticket = await Ticket.get(PydanticObjectId(ticket_id))
    
    if not ticket or ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    await ticket.delete()
    return {"message": "Ticket deleted successfully"}

