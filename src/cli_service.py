import redis
import json
import uuid
from dotenv import load_dotenv
from datetime import datetime, timezone
import os
from redis_client import r, publish, subscribe

# Query and simulated uploads

def submit_image(path: str, source: str):
    image_id = str(uuid.uuid4()) # Simulated, for now

    publish("image.submitted", {
        "type": "publish",
        "topic": "image.submitted",
        "event_id": str(uuid.uuid4()),
        "payload": {
            "image_id": image_id,
            "path": path,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })
    print(f"[cli_service] Submitted image {image_id} from {source}")
    return image_id

def submit_query(query_text: str):
    # Simulate search
    query_id = str(uuid.uuid4())

    publish("query.submitted", {
        "type": "publish",
        "topic": "query.submitted",
        "event_id": str(uuid.uuid4()),
        "payload": {
            "query_id": query_id,
            "query_text": query_text,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })
    print(f"[cli_service] Submitted query: '{query_text}'")
    return query_id

def handle_query_completed(message):
    # Listen for results of query
    if message["type"] != "message":
        return

    try:
        data = json.loads(message["data"].decode("utf-8"))
        payload = data["payload"]
        print(f"\n[cli_service] Query results for '{payload['query_text']}':")
        for result in payload.get("results", []):
            print(f"  - {result['image_id']} (score: {result['score']:.3f})")
    except (KeyError, json.JSONDecodeError) as e:
        # Handle bad event gracefully
        print(f"[cli_service] Bad result event, ignoring: {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 cli_service.py upload <path> <source>")
        print("       python3 cli_service.py search <query>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "upload":
        path = sys.argv[2] if len(sys.argv) > 2 else "images/test.jpg"
        source = sys.argv[3] if len(sys.argv) > 3 else "camera_A"
        submit_image(path, source)
    elif command == "search":
        query = " ".join(sys.argv[2:])
        # Subscribe
        import threading
        t = threading.Thread(
            target=subscribe,
            args=("query.completed", handle_query_completed),
            daemon=True
        )
        t.start()
        submit_query(query)
        input("Press Enter to exit...\n")

