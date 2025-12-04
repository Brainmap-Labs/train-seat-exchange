from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List
from datetime import datetime
from beanie import PydanticObjectId

from app.core.security import get_current_user
from app.models.user import User
from app.models.exchange import ExchangeRequest
from app.models.message import Message

router = APIRouter()

class SendMessageRequest(BaseModel):
    content: str

@router.get("/{exchange_id}")
async def get_messages(
    exchange_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all messages for an exchange"""
    exchange = await ExchangeRequest.get(PydanticObjectId(exchange_id))
    
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange not found"
        )
    
    # Verify user is part of exchange
    if exchange.requester_id != current_user.id and exchange.target_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these messages"
        )
    
    messages = await Message.find(
        Message.exchange_id == PydanticObjectId(exchange_id)
    ).sort("+created_at").to_list()
    
    # Mark messages as read
    for msg in messages:
        if msg.sender_id != current_user.id and not msg.is_read:
            msg.is_read = True
            await msg.save()
    
    return [
        {
            "id": str(m.id),
            "sender_id": str(m.sender_id),
            "content": m.content,
            "is_read": m.is_read,
            "created_at": m.created_at,
        }
        for m in messages
    ]

@router.post("/{exchange_id}")
async def send_message(
    exchange_id: str,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """Send a message in an exchange chat"""
    exchange = await ExchangeRequest.get(PydanticObjectId(exchange_id))
    
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange not found"
        )
    
    # Verify user is part of exchange
    if exchange.requester_id != current_user.id and exchange.target_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to send messages here"
        )
    
    # Create message
    message = Message(
        exchange_id=PydanticObjectId(exchange_id),
        sender_id=current_user.id,
        content=request.content,
    )
    await message.insert()
    
    # TODO: Send real-time notification via WebSocket
    
    return {
        "id": str(message.id),
        "sender_id": str(message.sender_id),
        "content": message.content,
        "created_at": message.created_at,
    }

