import redis
import json
from dotenv import load_dotenv
import os
from redis_client import r



def handle_message(message):
    if message["type"] == "pmessage":
        data = json.loads(message["data"])
        topic = data["topic"]

        if topic == "image.submitted":
            print("Image submitted!")

pubsub = r.pubsub()
pubsub.psubscribe("image.*")
print("CLI listening...")
for message in pubsub.listen():
    handle_message(message)


