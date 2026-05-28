from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId

from app.core.security import get_current_user
from app.core.security import get_admin_user
from app.models.user import User
from app.models.ticket import Ticket
from app.models.match import MatchSuggestion
from app.models.exchange import ExchangeRequest
from app.services.matching_service import MatchingService
from app.services.exchange_service import (
    create_exchange_request,
    format_exchange_request,
    get_exchange_for_user,
    expire_request_if_needed,
    ACTIVE_CHAT_STATUSES,
)

router = APIRouter()

class ExchangePreferences(BaseModel):
    same_coach_only: bool = False
    same_bay_only: bool = False
    berth_type_preferences: List[str] = []

class SendExchangeRequest(BaseModel):
    requester_ticket_id: str
    target_user_id: str
    target_ticket_id: str
    give_seats: List[dict]
    receive_seats: List[dict]
    message: Optional[str] = None

@router.post("/find-matches/{ticket_id}")
async def find_exchange_matches(
    ticket_id: str,
    preferences: Optional[ExchangePreferences] = None,
    use_ai_enhancement: bool = Query(False, description="Enable AI-powered matching optimization"),
    current_user: User = Depends(get_current_user)
):
    """Find potential exchange matches for a ticket
    
    Args:
        ticket_id: The ticket ID to find matches for
        preferences: Optional user preferences for filtering
        use_ai_enhancement: If True, uses AI (OpenAI or Gemini) to enhance match ranking
    """
    ticket = await Ticket.get(PydanticObjectId(ticket_id))
    
    if not ticket or ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    matching_service = MatchingService()

    # If there are stored suggestions for this ticket and preferences do not force live, return stored
    stored = await MatchSuggestion.find_one(MatchSuggestion.ticket_id == str(ticket.id))
    if stored and not (preferences and getattr(preferences, "berth_type_preferences", None)):
        # Return stored suggestions as prepopulated result
        return {
            "ticket_id": ticket_id,
            "matches": stored.suggestions,
            "total_matches": len(stored.suggestions),
            "prepopulated": True,
            "ai_enhanced": False
        }

    # Otherwise compute live
    matches = await matching_service.find_matches(
        ticket=ticket,
        preferences=preferences.model_dump() if preferences else {},
        use_ai_enhancement=use_ai_enhancement
    )
    
    return {
        "ticket_id": ticket_id,
        "matches": matches,
        "total_matches": len(matches),
        "ai_enhanced": use_ai_enhancement
    }


@router.post("/admin/run-matching")
async def admin_run_matching(
    train_number: Optional[str] = Query(None),
    travel_date: Optional[datetime] = Query(None),
    min_store_score: float = Query(60.0, description="Minimum score to store suggestion"),
    current_admin: bool = Depends(get_admin_user)
):
    """Admin endpoint to run matching across tickets and store good suggestions.

    If `train_number` and `travel_date` are provided, limit to that trip; otherwise run for all active tickets.
    Stores suggestions with `match_score >= min_store_score` in `match_suggestions` collection.
    """
    # Fetch tickets to process
    query = {}
    if train_number:
        query["train_number"] = train_number
    if travel_date:
        query["travel_date"] = travel_date

    tickets = await Ticket.find({}).to_list() if not query else await Ticket.find(
        Ticket.train_number == train_number,
        Ticket.travel_date == travel_date,
        Ticket.status == "active"
    ).to_list()

    matching_service = MatchingService()

    stored_count = 0
    for ticket in tickets:
        t_id = str(ticket.id)
        # Build preferences from ticket fields
        prefs = {
            "preferred_berth": ticket.preferred_berth or [],
            "allow_cyclic": ticket.allow_cyclic,
            "same_coach_only": ticket.same_coach_only,
            "same_bay_only": ticket.same_bay_only,
        }
        matches = await matching_service.find_matches(ticket=ticket, preferences=prefs)
        # Keep only suggestions >= min_store_score
        to_store = [m for m in matches if m.get("match_score", 0) >= min_store_score]
        if not to_store:
            # remove any existing stored suggestions
            existing = await MatchSuggestion.find_one(MatchSuggestion.ticket_id == t_id)
            if existing:
                await existing.delete()
            continue

        # Persist suggestions
        suggestion = await MatchSuggestion.find_one(MatchSuggestion.ticket_id == t_id)
        payload = [
            {
                "ticket_id": m.get("ticket_id", t_id),
                "other_ticket_id": m.get("ticket_id"),
                "user_id": m.get("user_id"),
                "user_name": m.get("user_name"),
                "match_score": m.get("match_score"),
                "benefit_description": m.get("benefit_description"),
                "available_seats": m.get("available_seats"),
                "type": m.get("type", "pairwise"),
            }
            for m in to_store
        ]
        if suggestion:
            suggestion.suggestions = payload
            suggestion.source = "admin_run"
            suggestion.created_at = suggestion.created_at
            await suggestion.save()
        else:
            suggestion = MatchSuggestion(
                ticket_id=t_id,
                train_number=ticket.train_number,
                travel_date=ticket.travel_date,
                suggestions=payload,
                source="admin_run",
            )
            await suggestion.insert()

        stored_count += 1

    return {"processed_tickets": len(tickets), "stored_suggestions": stored_count}


@router.post("/admin/run-global-matching")
async def admin_run_global_matching(
        train_number: str = Query(...),
        travel_date: datetime = Query(...),
        min_store_score: float = Query(60.0),
        time_limit: int = Query(30, description="ILP time limit seconds"),
        current_admin: bool = Depends(get_admin_user)
):
        """Run a global ILP optimizer across all tickets for a train+date and store cycle suggestions."""
        tickets = await Ticket.find(
                Ticket.train_number == train_number,
                Ticket.travel_date == travel_date,
                Ticket.status == "active",
        ).to_list()

        matching_service = MatchingService()
        cycles = matching_service.global_cycle_ilp(tickets, {}, time_limit_seconds=time_limit)

        stored = 0
        for cyc in cycles:
                # persist each ticket's suggestion from cycle
                cycle_ticket_ids = [str(t.id) for t in cyc["tickets"]]
                total = cyc.get("total_score", 0)
                if total < min_store_score:
                        continue
                # create payload entries for each ticket
                for t in cyc["tickets"]:
                        t_id = str(t.id)
                        payload = [{
                                "ticket_id": t_id,
                                "cycle_tickets": cycle_ticket_ids,
                                "match_score": total,
                                "benefit_description": cyc.get("description"),
                                "type": "global_cycle",
                        }]
                        suggestion = await MatchSuggestion.find_one(MatchSuggestion.ticket_id == t_id)
                        if suggestion:
                                suggestion.suggestions = payload
                                suggestion.source = "admin_global_ilp"
                                await suggestion.save()
                        else:
                                suggestion = MatchSuggestion(
                                        ticket_id=t_id,
                                        train_number=train_number,
                                        travel_date=travel_date,
                                        suggestions=payload,
                                        source="admin_global_ilp",
                                )
                                await suggestion.insert()
                stored += len(cycle_ticket_ids)

        return {"cycles_found": len(cycles), "tickets_updated": stored}


@router.post("/admin/preview-global-matching")
async def admin_preview_global_matching(
        train_number: str = Query(...),
        travel_date: datetime = Query(...),
        time_limit: int = Query(30, description="ILP time limit seconds"),
        current_admin: bool = Depends(get_admin_user)
    ):
        """Preview ILP-selected cycles for a train+date without persisting."""
        tickets = await Ticket.find(
            Ticket.train_number == train_number,
            Ticket.travel_date == travel_date,
            Ticket.status == "active",
        ).to_list()

        matching_service = MatchingService()
        cycles = matching_service.global_cycle_ilp(tickets, {}, time_limit_seconds=time_limit)

        # Return lightweight info
        out = []
        for cyc in cycles:
            out.append({
                "ticket_ids": [str(t.id) for t in cyc["tickets"]],
                "total_score": cyc["total_score"],
                "description": cyc.get("description"),
                "length": len(cyc["tickets"]),
            })

        return {"cycles": out, "count": len(out)}


@router.get("/admin/available-trips")
async def admin_available_trips(current_admin: bool = Depends(get_admin_user)):
        """Return list of available train_number + travel_date combos from active tickets."""
        tickets = await Ticket.find(Ticket.status == "active").to_list()
        combos = {}
        for t in tickets:
            combos.setdefault(t.train_number, set()).add(t.travel_date.isoformat())

        out = []
        for train, dates in combos.items():
            out.append({"train_number": train, "dates": sorted(list(dates))})

        return {"trips": out}


@router.get("/admin/ui")
async def admin_ui(current_admin: bool = Depends(get_admin_user)):
        html = """
        <!doctype html>
        <html>
        <head><title>Admin Matching</title></head>
        <body>
            <h1>Admin Matching Console</h1>
            <div>
                <h3>Run matching (per-ticket)</h3>
                <button id="run">Run Matching</button>
            </div>
            <div>
                <h3>Run global ILP matching</h3>
                <label>Train number: <input id="train" value="12301"></label>
                <label>Travel date (ISO): <input id="date" value=""></label>
                <button id="run-global">Run Global ILP</button>
            </div>
            <div>
                <h3>View stored matches for ticket</h3>
                <input id="ticket" placeholder="ticket id">
                <button id="view">View</button>
                <pre id="out"></pre>
            </div>
            <script>
                document.getElementById('run-global').addEventListener('click', async ()=>{
                    const train = document.getElementById('train').value;
                    const date = document.getElementById('date').value;
                    if(!train || !date){alert('Provide train and date');return}
                    const res = await fetch('/api/admin/run-global-matching?train_number='+encodeURIComponent(train)+'&travel_date='+encodeURIComponent(date),{method:'POST', headers:{'X-Admin-Key': prompt('Admin key')} });
                    const j = await res.json();
                    document.getElementById('out').innerText = JSON.stringify(j, null, 2);
                })

                document.getElementById('view').addEventListener('click', async ()=>{
                    const t = document.getElementById('ticket').value;
                    if(!t){alert('Ticket id required');return}
                    const res = await fetch('/api/admin/matches/'+encodeURIComponent(t),{headers:{'X-Admin-Key': prompt('Admin key')}});
                    const j = await res.json();
                    document.getElementById('out').innerText = JSON.stringify(j, null, 2);
                })
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html, status_code=200)


@router.get("/admin/matches/{ticket_id}")
async def admin_get_stored_matches(ticket_id: str, current_admin: bool = Depends(get_admin_user)):
    suggestion = await MatchSuggestion.find_one(MatchSuggestion.ticket_id == ticket_id)
    if not suggestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No stored suggestions")
    return {"ticket_id": ticket_id, "matches": suggestion.suggestions, "count": len(suggestion.suggestions)}


@router.post("/tickets/{ticket_id}/preferences")
async def update_ticket_preferences(
    ticket_id: str,
    prefs: ExchangePreferences,
    current_user: User = Depends(get_current_user)
):
    """Update ticket-level matching preferences and optionally rerun matching."""
    ticket = await Ticket.get(PydanticObjectId(ticket_id))
    if not ticket or ticket.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    ticket.preferred_berth = prefs.berth_type_preferences or None
    ticket.same_coach_only = prefs.same_coach_only
    ticket.same_bay_only = prefs.same_bay_only
    ticket.allow_cyclic = False
    await ticket.save()

    return {"message": "Preferences updated", "ticket_id": ticket_id}

@router.post("/batch-find-matches")
async def batch_find_matches(
    ticket_ids: List[str] = Query(..., description="List of ticket IDs to find matches for"),
    use_ai_enhancement: bool = Query(False, description="Enable AI-powered matching optimization"),
    current_user: User = Depends(get_current_user)
):
    """Find matches for multiple tickets at once (efficient for 10s of users)
    
    Args:
        ticket_ids: List of ticket IDs to process
        use_ai_enhancement: If True, uses AI (OpenAI or Gemini) to enhance match ranking
    """
    # Validate tickets belong to current user and retrieve them
    tickets = []
    for ticket_id in ticket_ids:
        ticket = await Ticket.get(PydanticObjectId(ticket_id))
        if not ticket or ticket.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to ticket {ticket_id}"
            )
        tickets.append(ticket)
    
    # Batch find matches
    matching_service = MatchingService()
    batch_results = await matching_service.batch_find_matches(
        tickets=tickets,
        use_ai_enhancement=use_ai_enhancement
    )
    
    # Format response
    formatted_results = {}
    for ticket_id, matches in batch_results.items():
        formatted_results[ticket_id] = {
            "matches": matches,
            "total_matches": len(matches),
            "ai_enhanced": use_ai_enhancement
        }
    
    return {
        "tickets_processed": len(tickets),
        "results": formatted_results,
        "ai_enhanced": use_ai_enhancement
    }

@router.post("/request")
async def send_exchange_request(
    request_data: SendExchangeRequest,
    current_user: User = Depends(get_current_user)
):
    """Send an exchange request to another user on the same train."""
    exchange_request = await create_exchange_request(
        requester=current_user,
        requester_ticket_id=request_data.requester_ticket_id,
        target_user_id=request_data.target_user_id,
        target_ticket_id=request_data.target_ticket_id,
        give_seats=request_data.give_seats,
        receive_seats=request_data.receive_seats,
        message=request_data.message,
    )

    return {
        "message": "Exchange request sent successfully",
        "request_id": str(exchange_request.id),
        "request": await format_exchange_request(exchange_request, current_user.id),
    }

@router.get("/requests")
async def get_exchange_requests(current_user: User = Depends(get_current_user)):
    """List exchange requests sent to or from the current user."""
    received_raw = await ExchangeRequest.find(
        ExchangeRequest.target_user_id == current_user.id
    ).sort("-created_at").to_list()

    sent_raw = await ExchangeRequest.find(
        ExchangeRequest.requester_id == current_user.id
    ).sort("-created_at").to_list()

    received = []
    for req in received_raw:
        req = await expire_request_if_needed(req)
        received.append(await format_exchange_request(req, current_user.id))

    sent = []
    for req in sent_raw:
        req = await expire_request_if_needed(req)
        sent.append(await format_exchange_request(req, current_user.id))

    return {"received": received, "sent": sent}


@router.get("/requests/{request_id}")
async def get_exchange_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get a single exchange request (for detail view and chat header)."""
    exchange_req = await get_exchange_for_user(request_id, current_user.id)
    return await format_exchange_request(exchange_req, current_user.id)


@router.post("/requests/{request_id}/cancel")
async def cancel_exchange_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
):
    """Cancel a pending request (requester only)."""
    exchange_req = await get_exchange_for_user(request_id, current_user.id)

    if exchange_req.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the requester can cancel this request",
        )

    if exchange_req.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel request with status: {exchange_req.status}",
        )

    exchange_req.status = "declined"
    exchange_req.updated_at = datetime.utcnow()
    await exchange_req.save()

    return {"message": "Exchange request cancelled", "status": exchange_req.status}

@router.post("/requests/{request_id}/accept")
async def accept_exchange_request(
    request_id: str,
    current_user: User = Depends(get_current_user)
):
    """Accept an exchange request (target user only)."""
    exchange_req = await get_exchange_for_user(request_id, current_user.id)

    if exchange_req.target_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the recipient can accept this request",
        )

    if exchange_req.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept request with status: {exchange_req.status}",
        )

    exchange_req.status = "accepted"
    exchange_req.updated_at = datetime.utcnow()
    await exchange_req.save()

    return {
        "message": "Exchange request accepted",
        "status": exchange_req.status,
        "request": await format_exchange_request(exchange_req, current_user.id),
    }

@router.post("/requests/{request_id}/decline")
async def decline_exchange_request(
    request_id: str,
    current_user: User = Depends(get_current_user)
):
    """Decline an exchange request (target user only)."""
    exchange_req = await get_exchange_for_user(request_id, current_user.id)

    if exchange_req.target_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the recipient can decline this request",
        )

    if exchange_req.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot decline request with status: {exchange_req.status}",
        )

    exchange_req.status = "declined"
    exchange_req.updated_at = datetime.utcnow()
    await exchange_req.save()

    return {
        "message": "Exchange request declined",
        "status": exchange_req.status,
    }

@router.post("/requests/{request_id}/complete")
async def complete_exchange(
    request_id: str,
    current_user: User = Depends(get_current_user)
):
    """Confirm the physical seat exchange was completed (both parties must confirm)."""
    exchange_req = await get_exchange_for_user(request_id, current_user.id)

    if exchange_req.status not in ACTIVE_CHAT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete request with status: {exchange_req.status}",
        )

    if exchange_req.requester_id == current_user.id:
        exchange_req.requester_confirmed = True
    elif exchange_req.target_user_id == current_user.id:
        exchange_req.target_confirmed = True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    if exchange_req.can_complete():
        exchange_req.status = "completed"
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
        "request": await format_exchange_request(exchange_req, current_user.id),
    }

