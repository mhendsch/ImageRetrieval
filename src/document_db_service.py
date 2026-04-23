import redis
import json
from dotenv import load_dotenv
import os
from redis_client import r, subscribe

def store_annotation(image_id: str, annotation: dict):
    # Use Redis hashing as a stand-in, replace with FAISS later
    r.hset("annotations", image_id, json.dumps(annotation))
    print(f" Stored annotation for {image_id}")

def get_annotation(image_id: str):
    raw = r.hget("annotations", image_id)
    if raw: # Don't return null annotation
        return json.loads(raw)
    return None 

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
            "camera": payload.get("source"),
            "objects": payload.get("objects", []),
            "history": ["submitted", "inference_completed"]
        }

        store_annotation(image_id, annotation)

        from redis_client import publish
        import uuid
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
    print("[document_db_service] Listening on inference.completed...")
    subscribe("inference.completed", handle_inference_completed)