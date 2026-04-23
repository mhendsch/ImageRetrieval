import redis
import json
from dotenv import load_dotenv
import os
from redis_client import r

def store_annotation(image_id: str, annotation: dict):
    # Use Redis hashing as a stand-in, replace with FAISS later
    r.hset("annotations", image_id, json.dumps(annotation))
    print(f" Stored aotation for {image_id}")

def get_annotation(image_id: str):
    raw = r.hget("annotations", image_id)
    if raw: # Don't return null annotation
        return json.loads(raw)
    return None 

def handle_inference_completed(message):
    return

if __name__ == "__main__":
    print("[document_db_service] Listening on inference.completed...")
    subscribe("inference.completed", handle_inference_completed)