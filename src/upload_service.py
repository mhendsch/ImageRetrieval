import redis
import json
from dotenv import load_dotenv
import os
from redis_client import r

TOPIC = "image.submitted"

# Publish that image had been uploaded
def publish_image_submitted(image_id: str, path: str, source: str):
    event = {
        "type": "publish",
        "topic": TOPIC,
        "event_id": str(uuid.uuid4()),
        "payload": {
            "image_id": image_id,
            "path": path,
            "source": source, 
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
    r.publish(TOPIC, json.dumps(event))
    return event

def upload_image(image_id: str, path: str, source: str):
    return publish_image_submitted(image_id, path, source)



