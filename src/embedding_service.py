import redis
import json
from dotenv import load_dotenv
import os
from redis_client import r, subscribe, publish
import uuid
import random
import torch
import clip
import traceback

EMBEDDING_DIM = 512

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
model.eval()

# Real embedding logic
def get_text_embedding(query_text: str) -> list[float]:
    # Embed text using CLIP so it's comparable to image embedding
    text = clip.tokenize([query_text]).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text)
        text_features /= text_features.norm(dim=-1, keepdim=True)
    return text_features.cpu().numpy()[0].tolist()

def get_image_embedding(path: str) -> list[float]:
    from PIL import Image
    image = preprocess(Image.open(path)).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(image)
        image_features /= image_features.norm(dim=-1, keepdim=True)
    return image_features.cpu().numpy()[0].tolist()

# Simulated embeddings
def simulate_embedding(image_id: str) -> list[float]:
    # Simulate an embedding for now
    rng = random.Random(image_id)
    return [rng.uniform(-1,1) for _ in range(EMBEDDING_DIM)]


def store_embedding(image_id: str, vector: list[float], path: str = ""):
    r.hset("embeddings", image_id, json.dumps({"vector": vector, "path": path}))
    print(f"[embedding_service] Stored embedding for {image_id}")

def get_embedding(image_id: str) -> list[float] | None:
    raw = r.hget("embeddings", image_id)
    if raw:
        entry = json.loads(raw)
        return entry["vector"]
    return None

def get_all_embeddings() -> dict[str, dict]:
    all_raw = r.hgetall("embeddings")
    return {
        image_id: json.loads(v)
        for image_id, v in all_raw.items()
    }

def handle_annotation_stored(message):
    if message["type"] != "message":
        return
    try:
        data = json.loads(message["data"])
        payload = data["payload"]
        image_id = payload["image_id"]

        # Don't double embed
        if get_embedding(image_id):
            print(f"[embedding_service] Already have embedding for {image_id}, ignoring")
            return
        
        # Simulate embedding
        #vector = simulate_embedding(image_id)
        #store_embedding(image_id, vector)

        # Actual embedding
        path = payload["annotation"]["path"]

        if os.path.exists(path):
            vector = get_image_embedding(path)
        else:
            print(f"[embedding_service] Path not found, using simulated embedding")
            vector = simulate_embedding(image_id)
        
        store_embedding(image_id, vector, path)

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
    if message["type"] != "message":
        return

    try:
        data = json.loads(message["data"])
        payload = data["payload"]
        query_id = payload["query_id"]
        query_text = payload.get("query_text")
        query_path = payload.get("query_path")

        # Simulate a query embedding
        # query_vector = simulate_embedding(query_text)
        
        # Get actual embedding
        if query_text != None:
            query_vector = get_text_embedding(query_text)
        elif query_path != None:
            query_vector = get_image_embedding(query_path)
        
        vector_store = get_all_embeddings()

        # Cosine similarity (credit: Claude), for simulation only
        results = []
        for image_id, entry in vector_store.items():
            vector = entry["vector"]
            path = entry.get("path", "unkown")
            score = cosine_similarity(query_vector, vector)
            results.append({
                "image_id": image_id, 
                "path": path,
                "score": score
            })
        
        # Return top 5
        results.sort(key=lambda x: x["score"], reverse=True)
        top_k = results[:5]

        publish("query.completed", {
            "type": "publish",
            "topic": "query.completed",
            "event_id": str(uuid.uuid4()),
            "payload": {
                "query_id": query_id,
                "query_text": query_text,
                "results": top_k
            }
        })

    except (KeyError, json.JSONDecodeError) as e:
        traceback.print_exc()
        # Handle error
        print(f"[embedding_service] Bad query event, ignoring: {e}")

    return

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x ** 2 for x in a) ** 0.5
    mag_b = sum(x ** 2 for x in b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)



if __name__ == "__main__":
    import time
    time.sleep(1) # give time for Redis connection
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