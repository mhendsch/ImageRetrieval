import redis
import json
from dotenv import load_dotenv
import os
from redis_client import r, subscribe, publish
import uuid
import random

EMBEDDING_DIM = 128

def simulate_embedding(image_id: str) -> list[float]:
    # Simulate an embedding for now
    rng = random.Random(image_id)
    return [rng.uniform(-1,1) for _ in range(EMBEDDING_DIM)]

# Simulated FAISS
_vector_store: dict[str, list[float]] = {}

def store_embedding(image_id: str, vector: list[float]):
    _vector_store[image_id] = vector
    print(f"[embedding_service] Stored embedding for {image_id}")

def get_embedding(image_id: str):
    return _vector_store.get(image_id)

def handle_annotation_stored(message):
    if message["type"] != "message":
        return
    try:
        data = json.loads(message["data"].decode("utf-8"))
        payload = data["payload"]
        image_id = payload["image_id"]

        # Don't double embed
        if get_embedding(image_id):
            print(f"[embedding_service] Already have embedding for {image_id}, ignoring")
            return
        vector = simulate_embedding(image_id)
        store_embedding(image_id, vector)

        publish("embedding.created", {
            "type": "publish",
            "topic": "embedding.created",
            "event_id": str(uuid.uuid4()),
            "payload": {
                "image_id": image_id,
                "embedding_dim": EMBEDDING_DIM,
                "timestamp": payload.get("timestamp")
            }
        })
    
    except (KeyError, json.JSONDecodeError) as e:
        # Handle bad events
        print(f"[embedding_service] Bad event, ignoring: {e}")

def handle_query_submitted(message):
    return

if __name__ == "__main__":
    import threading
    print("[embedding_service] Listening on annotation.stored and query.submitted...")

    # Subscribe, learned this in EC440
    t = threading.Thread(
        target=subscribe, 
        args=("query.submitted", handle_query_submitted),
        daemon=True
    )
    t.start()

    subscribe("annotation.stored", handle_annotation_stored)