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

    mongodb_url = (settings.MONGODB_URL or "").strip()
    if not mongodb_url:
        raise RuntimeError(
            "MONGODB_URL is not set. "
            "For Docker/Render, pass it as an environment variable "
            "(e.g. docker run --env-file .env ... or set it in the Render dashboard). "
            "For local dev without Docker, use backend/.env. "
            "See backend/.env.example."
        )

    if not (
        mongodb_url.startswith("mongodb://")
        or mongodb_url.startswith("mongodb+srv://")
    ):
        preview = mongodb_url[:40] + ("..." if len(mongodb_url) > 40 else "")
        raise RuntimeError(
            "MONGODB_URL must start with mongodb:// or mongodb+srv://. "
            f"Got: {preview!r}. "
            "If your Atlas password contains #, $, or &, wrap the full URL in double quotes "
            'in backend/.env, e.g. MONGODB_URL="mongodb+srv://user:pass@host/?retryWrites=true&w=majority". '
            "URL-encode special characters in the password if needed."
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
