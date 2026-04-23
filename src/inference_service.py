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
    if message["type"] != "message":
        return
    
    try:
        data = json.loads(message["data"].decode("utf-8"))
        payload = data["payload"]
        image_id = payload["image_id"]

        # Check for double inference
        if image_id in _processed:
            print(f"[inference_service] Already processed {image_id}, ignoring")
            return
        
        print(f"[inference_service] Running inference on {image_id}...")
        objects = simulate_inference(image_id)
        _processed.add(image_id)

        publish("inference.completed", {
            "type": "publish",
            "topic": "inference.completed",
            "event_id": str(uuid.uuid4()),
            "payload": {
                "image_id": image_id,
                "path": payload["path"],
                "source": payload["source"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "objects": objects
            }
        })

        print(f"[inference_service] Published inference.completed for {image_id} "
              f"({len(objects)} objects detected)")

    except (KeyError, json.JSONDecodeError) as e:
        # Handle bad event
        print(f"[inference_service] Bad event, ignoring: {e}")


if __name__ == "__main__":
    print("[inference_service] Listening on image.submitted...")
    subscribe("image.submitted", handle_image_submitted)