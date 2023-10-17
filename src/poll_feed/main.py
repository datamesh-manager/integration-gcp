import os
import json
import functions_framework
import datameshmanager_client as dmm
from google.cloud import pubsub, secretmanager, firestore

publisher = pubsub.PublisherClient()
store = firestore.Client()


def get_last_event_id() -> str: 
    document = store.document("Test/last_event_id")
    value = document.get().get("id")
    return value


def set_last_event_id(last_id: str) -> None:
    document = store.document("Test/last_event_id")
    document.set({"id": last_id})


def publish_events(topic_name, events):
    for event in events:
        data = json.dumps(event).encode('utf-8')
        publisher.publish(topic_name, data=data)
    pass


@functions_framework.http
def main(event):
    client = dmm.DataMeshManagerClient(os.getenv("API_KEY"))

    last_id = get_last_event_id()

    data = client.get_events(last_id)
    topic_name = os.getenv("TOPIC")
    if data:
        publish_events(topic_name, data)
        last_id = data[-1]["id"]
        set_last_event_id(last_id)

    return "OK"
