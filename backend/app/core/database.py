import ssl
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
    # Configure SSL/TLS for MongoDB Atlas connection
    # For development: allow invalid certificates
    # For production: use proper SSL certificates
    
    # Motor client options
    client_options = {
        "serverSelectionTimeoutMS": 5000,
        "connectTimeoutMS": 10000,
    }
    
    # In development mode, allow invalid certificates using SSL context
    if settings.DEBUG:
        # Create SSL context that doesn't verify certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        client_options["tls"] = True
        client_options["tlsAllowInvalidCertificates"] = True
        # Alternative: use ssl_context directly
        # client_options["ssl"] = ssl_context
    
    client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        **client_options
    )
    
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[User, Ticket, ExchangeRequest, Message]
    )

async def get_database():
    return client[settings.DATABASE_NAME]

