import redis
import json
from dotenv import load_dotenv
import os
from redis_client import r, subscribe, publish
import uuid
from datetime import datetime, timezone
import random
import torch
import clip
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
model.eval()
# Simulated labels that could be detected
POSSIBLE_LABELS = ["car", "person", "truck", "bicycle", "motorcycle", "pedestrian", "bus", "train", "traffic"]

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

def actual_inference(image_id: str, path: str) -> list[dict]:

    image = preprocess(Image.open(path)).unsqueeze(0).to(device)
    text = clip.tokenize(POSSIBLE_LABELS).to(device)

    with torch.no_grad():
        logits_per_image, logits_per_text = model(image, text)
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

    # Build objects list
    objects = []
    for label, conf in zip(POSSIBLE_LABELS, probs):
        conf = float(conf)
        if conf > 0.1:
            objects.append({
                "label": label,
                "bbox": [],
                "conf": round(float(conf), 2)
            })
    
    objects.sort(key=lambda x: x["conf"], reverse=True)
    return objects

# Track which image ids have been processed
_processed: set[str] = set()

def handle_image_submitted(message):
    if message["type"] != "message":
        return
    
    try:
        data = json.loads(message["data"])
        payload = data["payload"]
        image_id = payload["image_id"]

        # Check for double inference
        if image_id in _processed:
            print(f"[inference_service] Already processed {image_id}, ignoring")
            return
        
        print(f"[inference_service] Running inference on {image_id}...")
        if os.path.exists(payload["path"]):
            objects = actual_inference(image_id, payload["path"])
        else:
            print(f"[inference_service] Path not found, using simulated inference")
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
              f"({len(objects)} objects detected):"
              f" {[obj['label'] for obj in objects]}")

    except (KeyError, json.JSONDecodeError) as e:
        # Handle bad event
        print(f"[inference_service] Bad event, ignoring: {e}")


if __name__ == "__main__":
    import time
    time.sleep(1) # give time for Redis connection
    print("[inference_service] Listening on image.submitted...")
    subscribe("image.submitted", handle_image_submitted)