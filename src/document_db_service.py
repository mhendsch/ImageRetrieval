import redis
import json
from dotenv import load_dotenv
import os
from redis_client import r, subscribe, publish
from pymongo import MongoClient
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB", "image_retrieval")]
annotations = db["annotations"]

"""
def store_annotation(image_id: str, annotation: dict):
    # Use Redis hashing as a stand-in, replace with FAISS later
    r.hset("annotations", image_id, json.dumps(annotation))
    print(f"[document_db_service] Stored annotation for {image_id}")
"""

def store_annotation(image_id: str, annotation: dict):
    # Should handle idempotency
    annotations.update_one(
        {"image_id": image_id},
        {"$set": annotation},
        upsert=True # insert if not exists
    )
    print(f"[document_db_service] Stored annotation for {image_id} in MongoDB")

def get_annotation(image_id: str) -> dict | None:
    result = annotations.find_one({"image_id": image_id}, {"_id": 0})
    return result

def get_all_annotations() -> list[dict]:
    all_raw = annotations.find({}, {"_id": 0})
    return list(all_raw)

def handle_inference_completed(message):
    # Listen for inference completed
    if message["type"] != "message":
        return
    
    try: 
        data = json.loads(message["data"])
        payload = data["payload"]
        image_id = payload["image_id"]

        # Build annotation
        annotation = {
            "image_id": image_id,
            "path": payload["path"],
            "camera": payload.get("source"),
            "objects": payload.get("objects", []),
            "history": ["submitted", "inference_completed"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        store_annotation(image_id, annotation)

        publish("annotation.stored", {
            "type": "publish",
            "topic": "annotation.stored",
            "event_id": str(uuid.uuid4()),
            "payload": {
                "image_id": image_id,
                "annotation": annotation
            }
        })

    except (KeyError, json.JSONDecodeError) as e:
        # Bad events handled robustly
        print(f"[document_db_service] Bad event, ignoring: {e}")
        
    return

if __name__ == "__main__":
    import time
    time.sleep(1) # give time for Redis connection
    print("[document_db_service] Listening on inference.completed...")
    subscribe("inference.completed", handle_inference_completed)