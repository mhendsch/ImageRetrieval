import redis
import json
from dotenv import load_dotenv
import os
from redis_client import r, subscribe, publish
import uuid
from datetime import datetime, timezone
import random

# Simulated labels that could be detected
POSSIBLE_LABELS = ["car", "person", "truck", "bicycle", "motorcycle", "pedestrian", "bus", "train"]

def simulate_inference(image_id: str) -> list[dict]:
    # Generate random classifications, seeded by image_id
    rng = random.Random(image_id)
    num_objects = rng.randint(1,5)

    objects = []
    for _ in range(num_objects):
        label = rng.choice(POSSIBLE_LABELS)
        x1 = rng.randint(0, 400)
        y1 = rng.randint(0, 400)
        x2 = x1 + rng.randint(50, 200)
        y2 = y1 + rng.randint(50, 200)
        conf = round(rng.uniform(0.7, 0.99), 2)
        objects.append({
            "label": label,
            "bbox": [x1, y1, x2, y2],
            "conf": conf
        })
    return objects

# Track which image ids have been processed
_processed: set[str] = set()

def handle_image_submitted(message):
    return

if __name__ == "__main__":
    print("[inference_service] Listening on image.submitted...")
    subscribe("image.submitted", handle_image_submitted)