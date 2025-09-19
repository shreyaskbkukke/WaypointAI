import os
import motor.motor_asyncio
from beanie import init_beanie
from dotenv import load_dotenv

from models.agent_builder import AgentBuilder

load_dotenv()

async def init_db() -> None:
    """
    Initialize MongoDB connection and register Beanie document models.
    """
    mongo_uri = os.getenv("MONGO_CONNECTION_STRING")
    mongo_db = os.getenv("MONGO_DB")

    if not mongo_uri or not mongo_db:
        raise ValueError("MONGO_CONNECTION_STRING and MONGO_DB must be set in environment variables.")

    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)

    await init_beanie(
        database=client[mongo_db],
        document_models=[
            AgentBuilder,
        ],
    )
