import redis
import json
from dotenv import load_dotenv
import os
from redis_client import r

"""success = r.set('foo', 'bar')
# True

result = r.get('foo')
print(result)"""

def handle_message(message):
    if message["type"] == "message":
        data = json.loads(message["data"])
        
        event_type = data["type"]       # "publish" or "status"
        topic = data["topic"]
        event_id = data["event_id"]
        #payload = data["payload"]       # image_id, path, source, timestamp

        print(f"Event ID: {event_id}")
        print(f"Type: {event_type} | Topic: {topic}")
        print(f"Payload: {payload}")

def publishMessage(my_channel, event_type, topic, event_id, payload):
    message = json.dumps({
        "type": event_type,       # "publish" or "status"
        "topic": topic,           # e.g. "image.submitted", "inference.completed"
        "event_id": event_id     # unique key
        "payload": {
            "image_id": payload["image_id"],
            "path": payload["path"],
            "source": payload["source"],
            "timestamp": payload["timestamp"]
       }
    })
    r.publish(channel=my_channel, message=message)

def subscribeToChannel(channel):
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    
    for message in pubsub.listen():
        handle_message(message)


publishMessage("image.submitted", "publish", "image.submitted", 123, "AH")
