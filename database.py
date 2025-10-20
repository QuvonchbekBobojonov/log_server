from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "log_db")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]


def init_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]


def close_db():
    global client
    if client:
        client.close()
