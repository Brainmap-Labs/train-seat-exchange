from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId

from app.core.security import get_current_user
from app.models.user import User
from app.models.ticket import Ticket
from app.models.exchange import ExchangeRequest, ExchangeProposal, SeatInfo
from app.services.matching_service import MatchingService

router = APIRouter()

class ExchangePreferences(BaseModel):
    same_coach_only: bool = False
    same_bay_only: bool = False
    berth_type_preferences: List[str] = []

class SendExchangeRequest(BaseModel):
    target_user_id: str
    target_ticket_id: str
    give_seats: List[dict]
    receive_seats: List[dict]
    message: Optional[str] = None

@router.post("/find-matches/{ticket_id}")
async def find_exchange_matches(
    ticket_id: str,
    preferences: Optional[ExchangePreferences] = None,
    current_user: User = Depends(get_current_user)
):
    """Find potential exchange matches for a ticket"""
    ticket = await Ticket.get(PydanticObjectId(ticket_id))
    
    if not ticket or ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Find matches using the matching service
    matching_service = MatchingService()
    matches = await matching_service.find_matches(
        ticket=ticket,
        preferences=preferences.model_dump() if preferences else {}
    )
    
    return {
        "ticket_id": ticket_id,
        "matches": matches,
        "total_matches": len(matches)
    }

@router.post("/request")
async def send_exchange_request(
    request_data: SendExchangeRequest,
    current_user: User = Depends(get_current_user)
):
    """Send an exchange request to another user"""
    # Validate target user and ticket
    target_user = await User.get(PydanticObjectId(request_data.target_user_id))
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )
    
    target_ticket = await Ticket.get(PydanticObjectId(request_data.target_ticket_id))
    if not target_ticket or target_ticket.user_id != target_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target ticket not found"
        )
    
    # Get requester's ticket (find by train and date)
    requester_ticket = await Ticket.find_one(
        Ticket.user_id == current_user.id,
        Ticket.train_number == target_ticket.train_number,
        Ticket.travel_date == target_ticket.travel_date
    )
    
    if not requester_ticket:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't have a ticket for this train"
        )
    
    # Create exchange proposal
    proposal = ExchangeProposal(
        give=[SeatInfo(**s) for s in request_data.give_seats],
        receive=[SeatInfo(**s) for s in request_data.receive_seats],
    )
    
    # Create exchange request
    exchange_request = ExchangeRequest(
        requester_id=current_user.id,
        requester_ticket_id=requester_ticket.id,
        target_user_id=target_user.id,
        target_ticket_id=target_ticket.id,
        train_number=target_ticket.train_number,
        travel_date=target_ticket.travel_date,
        proposal=proposal,
        message=request_data.message,
    )
    
    await exchange_request.insert()
    
    # TODO: Send notification to target user
    
    return {
        "message": "Exchange request sent successfully",
        "request_id": str(exchange_request.id)
    }

@router.get("/requests")
async def get_exchange_requests(current_user: User = Depends(get_current_user)):
    """Get all exchange requests for current user"""
    # Received requests
    received = await ExchangeRequest.find(
        ExchangeRequest.target_user_id == current_user.id
    ).to_list()
    
    # Sent requests
    sent = await ExchangeRequest.find(
        ExchangeRequest.requester_id == current_user.id
    ).to_list()
    
    async def format_request(req, is_received):
        other_user_id = req.requester_id if is_received else req.target_user_id
        other_user = await User.get(other_user_id)
        return {
            "id": str(req.id),
            "other_user": {
                "id": str(other_user.id),
                "name": other_user.name,
                "rating": other_user.rating,
            } if other_user else None,
            "train_number": req.train_number,
            "travel_date": req.travel_date,
            "proposal": req.proposal.model_dump(),
            "status": req.status,
            "message": req.message,
            "created_at": req.created_at,
        }
    
    return {
        "received": [await format_request(r, True) for r in received],
        "sent": [await format_request(r, False) for r in sent],
    }

@router.post("/requests/{request_id}/accept")
async def accept_exchange_request(
    request_id: str,
    current_user: User = Depends(get_current_user)
):
    """Accept an exchange request"""
    exchange_req = await ExchangeRequest.get(PydanticObjectId(request_id))
    
    if not exchange_req or exchange_req.target_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange request not found"
        )
    
    if exchange_req.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept request with status: {exchange_req.status}"
        )
    
    exchange_req.status = "accepted"
    exchange_req.updated_at = datetime.utcnow()
    await exchange_req.save()
    
    # TODO: Notify requester
    
    return {"message": "Exchange request accepted"}

@router.post("/requests/{request_id}/decline")
async def decline_exchange_request(
    request_id: str,
    current_user: User = Depends(get_current_user)
):
    """Decline an exchange request"""
    exchange_req = await ExchangeRequest.get(PydanticObjectId(request_id))
    
    if not exchange_req or exchange_req.target_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange request not found"
        )
    
    exchange_req.status = "declined"
    exchange_req.updated_at = datetime.utcnow()
    await exchange_req.save()
    
    return {"message": "Exchange request declined"}

@router.post("/requests/{request_id}/complete")
async def complete_exchange(
    request_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark exchange as completed"""
    exchange_req = await ExchangeRequest.get(PydanticObjectId(request_id))
    
    if not exchange_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange request not found"
        )
    
    # Check if current user is part of exchange
    if exchange_req.requester_id == current_user.id:
        exchange_req.requester_confirmed = True
    elif exchange_req.target_user_id == current_user.id:
        exchange_req.target_confirmed = True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # If both confirmed, mark as completed
    if exchange_req.can_complete():
        exchange_req.status = "completed"
        
        # Update exchange counts for both users
        requester = await User.get(exchange_req.requester_id)
        target = await User.get(exchange_req.target_user_id)
        if requester:
            requester.total_exchanges += 1
            await requester.save()
        if target:
            target.total_exchanges += 1
            await target.save()
    
    exchange_req.updated_at = datetime.utcnow()
    await exchange_req.save()
    
    return {
        "message": "Confirmation recorded",
        "status": exchange_req.status,
        "requester_confirmed": exchange_req.requester_confirmed,
        "target_confirmed": exchange_req.target_confirmed,
    }

