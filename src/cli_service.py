import redis
import json
from dotenv import load_dotenv
import os
import document_db_service
from redis_client import r



def handle_message(message):
    if message["type"] == "message":
        data = json.loads(message["data"])
        topic = data["topic"]

        if topic == "image.submitted":
            print("Image submitted!")

pubsub = r.pubsub()
pubsub.subscribe("image.submitted")
print("CLI listening...")
for message in pubsub.listen():
    handle_message(message)


