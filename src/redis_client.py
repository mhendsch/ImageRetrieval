import redis
from dotenv import load_dotenv
import os

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_URL"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True,
    username="default",
    password=os.getenv("REDIS_PASSWORD"),
)