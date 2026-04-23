import redis
from dotenv import load_dotenv
import os
import json

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_URL"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True,
    username="default",
    password=os.getenv("REDIS_PASSWORD"),
)

def publish(topic: str, event: dict):
    r.publish(topic, json.dumps(event))

def subscribe(topic: str, handler):
    pubsub = r.pubsub()
    pubsub.subscribe(**{topic: handler})
    #print(f"Subscribed to {topic}")
    for message in pubsub.listen():
        handler(message)