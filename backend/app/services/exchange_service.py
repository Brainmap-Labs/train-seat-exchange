"""Business logic for seat exchange requests."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from beanie import PydanticObjectId
from fastapi import HTTPException, status

from app.models.exchange import ExchangeRequest, ExchangeProposal, SeatInfo
from app.models.ticket import Ticket, Passenger
from app.models.user import User

ACTIVE_CHAT_STATUSES = frozenset({"pending", "accepted"})
TERMINAL_STATUSES = frozenset({"declined", "completed", "expired"})


def passenger_to_seat_info(passenger: Passenger) -> SeatInfo:
    return SeatInfo(
        passenger_id=passenger.id,
        passenger_name=passenger.name,
        coach=passenger.coach,
        seat_number=passenger.seat_number,
        berth_type=passenger.berth_type,
    )


def compute_expires_at(travel_date: datetime) -> datetime:
    """Requests expire before journey or after 7 days, whichever is sooner."""
    now = datetime.utcnow()
    travel_deadline = travel_date - timedelta(hours=6)
    week_deadline = now + timedelta(days=7)
    if travel_deadline <= now:
        return now + timedelta(hours=24)
    return min(travel_deadline, week_deadline)


def validate_seats_on_ticket(seats: List[SeatInfo], ticket: Ticket) -> None:
    passengers_by_id = {p.id: p for p in ticket.passengers}
    for seat in seats:
        passenger = passengers_by_id.get(seat.passenger_id)
        if not passenger:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Passenger {seat.passenger_id} not found on ticket",
            )
        if (
            passenger.coach.upper() != seat.coach.upper()
            or passenger.seat_number != seat.seat_number
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seat details do not match the ticket",
            )


async def expire_request_if_needed(request: ExchangeRequest) -> ExchangeRequest:
    if (
        request.status == "pending"
        and request.expires_at
        and datetime.utcnow() > request.expires_at
    ):
        request.status = "expired"
        request.updated_at = datetime.utcnow()
        await request.save()
    return request


async def get_exchange_for_user(
    request_id: str, user_id: PydanticObjectId
) -> ExchangeRequest:
    request = await ExchangeRequest.get(PydanticObjectId(request_id))
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange request not found",
        )
    if request.requester_id != user_id and request.target_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this exchange",
        )
    return await expire_request_if_needed(request)


async def format_exchange_request(
    request: ExchangeRequest, viewer_id: PydanticObjectId
) -> Dict[str, Any]:
    is_received = request.target_user_id == viewer_id
    other_user_id = request.requester_id if is_received else request.target_user_id
    other_user = await User.get(other_user_id)

    return {
        "id": str(request.id),
        "role": "target" if is_received else "requester",
        "requester_id": str(request.requester_id),
        "requester_ticket_id": str(request.requester_ticket_id),
        "target_user_id": str(request.target_user_id),
        "target_ticket_id": str(request.target_ticket_id),
        "other_user": {
            "id": str(other_user.id),
            "name": other_user.name,
            "rating": other_user.rating,
        }
        if other_user
        else None,
        "train_number": request.train_number,
        "travel_date": request.travel_date,
        "proposal": request.proposal.model_dump(),
        "status": request.status,
        "message": request.message,
        "requester_confirmed": request.requester_confirmed,
        "target_confirmed": request.target_confirmed,
        "can_chat": request.status in ACTIVE_CHAT_STATUSES,
        "expires_at": request.expires_at,
        "created_at": request.created_at,
        "updated_at": request.updated_at,
    }


async def create_exchange_request(
    *,
    requester: User,
    requester_ticket_id: str,
    target_user_id: str,
    target_ticket_id: str,
    give_seats: List[dict],
    receive_seats: List[dict],
    message: Optional[str] = None,
) -> ExchangeRequest:
    if str(requester.id) == target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send an exchange request to yourself",
        )

    target_user = await User.get(PydanticObjectId(target_user_id))
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found",
        )

    requester_ticket = await Ticket.get(PydanticObjectId(requester_ticket_id))
    if not requester_ticket or requester_ticket.user_id != requester.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your ticket was not found",
        )

    target_ticket = await Ticket.get(PydanticObjectId(target_ticket_id))
    if not target_ticket or target_ticket.user_id != target_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target ticket not found",
        )

    if requester_ticket.status != "active" or target_ticket.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both tickets must be active to request an exchange",
        )

    if (
        requester_ticket.train_number != target_ticket.train_number
        or requester_ticket.travel_date != target_ticket.travel_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tickets must be for the same train and travel date",
        )

    give = [SeatInfo(**s) for s in give_seats]
    receive = [SeatInfo(**s) for s in receive_seats]
    if not give or not receive:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Proposal must include seats you offer and seats you want",
        )

    validate_seats_on_ticket(give, requester_ticket)
    validate_seats_on_ticket(receive, target_ticket)

    duplicate = await ExchangeRequest.find_one(
        ExchangeRequest.requester_id == requester.id,
        ExchangeRequest.target_user_id == target_user.id,
        ExchangeRequest.requester_ticket_id == requester_ticket.id,
        ExchangeRequest.target_ticket_id == target_ticket.id,
        ExchangeRequest.status == "pending",
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending request already exists for this exchange",
        )

    exchange_request = ExchangeRequest(
        requester_id=requester.id,
        requester_ticket_id=requester_ticket.id,
        target_user_id=target_user.id,
        target_ticket_id=target_ticket.id,
        train_number=target_ticket.train_number,
        travel_date=target_ticket.travel_date,
        proposal=ExchangeProposal(give=give, receive=receive),
        message=message.strip() if message else None,
        expires_at=compute_expires_at(target_ticket.travel_date),
    )
    await exchange_request.insert()
    return exchange_request
