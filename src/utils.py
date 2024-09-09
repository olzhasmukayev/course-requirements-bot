import os
import json
import logging
import redis

logger = logging.getLogger()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

def load_json(file: str) -> dict:
    try:
        with open(file, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {file}: {e}")
        return {}

def load_data():
    database = load_json("data/data.json")
    credits = load_json("data/credits.json")
    return database, credits

async def load_user_state(user_id: int) -> dict:
    """Load the user state from Redis."""
    try:
        state = r.get(f"user_state:{user_id}")
        return json.loads(state) if state else {}
    except Exception as e:
        logger.error(f"Error loading user state from Redis: {e}")
        return {}

async def save_user_state(user_id: int, state: dict):
    """Save the user state to Redis."""
    try:
        r.set(f"user_state:{user_id}", json.dumps(state))
    except Exception as e:
        logger.error(f"Error saving user state to Redis: {e}")
