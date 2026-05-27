from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings
from app.models.user import User
from app.models.ticket import Ticket
from app.models.exchange import ExchangeRequest
from app.models.message import Message

_BACKEND_DIR = Path(__file__).resolve().parents[2]

client: AsyncIOMotorClient = None


async def init_db():
    global client

    mongodb_url = (settings.MONGODB_URL or "").strip()
    if not mongodb_url:
        raise RuntimeError(
            "MONGODB_URL is empty. Set it in backend/.env "
            f"(expected file: {_BACKEND_DIR / '.env'}). See backend/.env.example."
        )

    client_options = {
        "serverSelectionTimeoutMS": 5000,
        "connectTimeoutMS": 10000,
    }

    # Atlas (mongodb+srv) uses TLS; local mongodb:// does not
    if settings.DEBUG and mongodb_url.startswith("mongodb+srv://"):
        client_options["tls"] = True
        client_options["tlsAllowInvalidCertificates"] = True

    client = AsyncIOMotorClient(mongodb_url, **client_options)

    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[User, Ticket, ExchangeRequest, Message],
    )


async def get_database():
    return client[settings.DATABASE_NAME]
