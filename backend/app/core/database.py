from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings
from app.models.user import User
from app.models.ticket import Ticket
from app.models.exchange import ExchangeRequest
from app.models.message import Message

client: AsyncIOMotorClient = None

async def init_db():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[User, Ticket, ExchangeRequest, Message]
    )

async def get_database():
    return client[settings.DATABASE_NAME]

