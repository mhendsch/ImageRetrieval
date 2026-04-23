import redis
import json
import uuid
from dotenv import load_dotenv
from datetime import datetime, timezone
import os
from redis_client import r, publish, subscribe

# Query and simulated uploads

def submit_image(path: str, source: str):
    image_id = str(uuid.uuid4()) # Simulated, for now

    publish("image.submitted", {
        "type": "publish",
        "topic": "image.submitted",
        "event_id": str(uuid.uuid4())
        "payload": {
            "image_id": image_id,
            "path": path,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })
    print(f"[cli_service] Submitted image {image_id} from {source}")
    return image_id

def submit_query():
    return

def handle_query_completed(message):
    return

