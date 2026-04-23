import redis
import json
from dotenv import load_dotenv
import os
from redis_client import r, subscribe, publish
import uuid
from datetime import datetime, timezone

# Simulated labels that could be detected
POSSIBLE_LABELS = ["car", "person", "truck", "bicycle", "motorcycle", "pedestrian", "bus", "train"]

def simulate_inference(image_id: str) -> list[dict]:
    return

# Track which image ids have been processed
_processed: set[str] = set()

def handle_image_submitted(message):
    return

if __name__ == "__main__":
    print("[inference_service] Listening on image.submitted...")
    subscribe("image.submitted", handle_image_submitted)