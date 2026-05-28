from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List
from beanie import PydanticObjectId

from app.core.security import get_current_user
from app.models.user import User
from app.models.message import Message
from app.services.exchange_service import (
    get_exchange_for_user,
    ACTIVE_CHAT_STATUSES,
)

router = APIRouter()

MAX_MESSAGE_LENGTH = 2000


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=MAX_MESSAGE_LENGTH)


@router.get("/{exchange_id}")
async def get_messages(
    exchange_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all messages for an exchange (marks others' messages as read)."""
    exchange = await get_exchange_for_user(exchange_id, current_user.id)

    messages = await Message.find(
        Message.exchange_id == PydanticObjectId(exchange_id)
    ).sort("+created_at").to_list()

    for msg in messages:
        if msg.sender_id != current_user.id and not msg.is_read:
            msg.is_read = True
            await msg.save()

    return {
        "exchange_id": exchange_id,
        "exchange_status": exchange.status,
        "can_send": exchange.status in ACTIVE_CHAT_STATUSES,
        "messages": [
            {
                "id": str(m.id),
                "sender_id": str(m.sender_id),
                "content": m.content,
                "is_read": m.is_read,
                "created_at": m.created_at,
            }
            for m in messages
        ],
    }


@router.post("/{exchange_id}")
async def send_message(
    exchange_id: str,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """Send a message in an exchange chat."""
    exchange = await get_exchange_for_user(exchange_id, current_user.id)

    if exchange.status not in ACTIVE_CHAT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot send messages for exchange with status: {exchange.status}",
        )

    content = request.content.strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    message = Message(
        exchange_id=PydanticObjectId(exchange_id),
        sender_id=current_user.id,
        content=content,
    )
    await message.insert()

    return {
        "id": str(message.id),
        "sender_id": str(message.sender_id),
        "content": message.content,
        "is_read": message.is_read,
        "created_at": message.created_at,
    }
