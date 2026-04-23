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
        "event_id": str(uuid.uuid4()),
        "payload": {
            "image_id": image_id,
            "path": path,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })
    print(f"[cli_service] Submitted image {image_id} from {source}")
    return image_id

def submit_query(query_text: str):
    # Simulate search
    query_id = str(uuid.uuid4())

    publish("query.submitted", {
        "type": "publish",
        "topic": "query.submitted",
        "event_id": str(uuid.uuid4()),
        "payload": {
            "query_id": query_id,
            "query_text": query_text,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })
    print(f"[cli_service] Submitted query: '{query_text}'")
    return query_id

def handle_query_completed(message):
    return

