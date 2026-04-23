import redis
import json
from dotenv import load_dotenv
import os
from redis_client import r, subscribe, publish
import uuid

def simulate_embedding(image_id: str) -> list[float]:
    return

# Simulated FAISS
_vector_store: dict[str, list[float]] = {}

def store_embedding(image_id: str, vector: list[float]):
    return

def get_embedding(image_id: str):
    return

def handle_annotation_stored(message):
    return

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